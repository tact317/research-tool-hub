from __future__ import annotations

import os
import shutil
import signal
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TextIO

from research_tool_hub.models import AppManifest, DependencySpec, LaunchProfile, ProcessStep
from research_tool_hub.paths import hub_root, logs_dir


@dataclass(slots=True)
class DependencyResult:
    dependency: DependencySpec
    ok: bool
    resolved: str = ""
    message: str = ""


@dataclass(slots=True)
class ManagedProcess:
    step: ProcessStep
    process: subprocess.Popen[bytes]
    log_stream: TextIO


@dataclass(slots=True)
class RunningApp:
    manifest: AppManifest
    profile: LaunchProfile
    app_root: Path
    processes: list[ManagedProcess] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    error: str | None = None

    @property
    def is_running(self) -> bool:
        return any(item.process.poll() is None for item in self.processes)


class ProcessManager:
    def __init__(self) -> None:
        self._running: dict[str, RunningApp] = {}
        self._lock = threading.RLock()

    def resolve_app_root(self, manifest: AppManifest, override: str | None = None) -> Path:
        if override:
            return Path(os.path.expandvars(override)).expanduser().resolve()
        configured = Path(os.path.expandvars(manifest.application_root)).expanduser()
        if not configured.is_absolute():
            configured = hub_root() / configured
        return configured.resolve()

    def _expand(self, value: str, app_root: Path) -> str:
        expanded = value.replace("${APP_ROOT}", str(app_root))
        expanded = expanded.replace("${HUB_ROOT}", str(hub_root()))
        return os.path.expandvars(os.path.expanduser(expanded))

    def _resolve_executable(self, value: str, app_root: Path) -> str:
        expanded = self._expand(value, app_root)
        candidate = Path(expanded)
        if candidate.is_absolute():
            return str(candidate)
        if any(separator in expanded for separator in ("/", "\\")) or expanded.startswith("."):
            return str((app_root / candidate).resolve())
        return shutil.which(expanded) or expanded

    def _resolve_working_directory(self, value: str, app_root: Path) -> Path:
        expanded = Path(self._expand(value, app_root))
        if expanded.is_absolute():
            return expanded
        return (app_root / expanded).resolve()

    def check_dependencies(
        self, manifest: AppManifest, app_root: Path
    ) -> list[DependencyResult]:
        results: list[DependencyResult] = []
        for dependency in manifest.dependencies:
            value = self._expand(dependency.value, app_root)
            if dependency.kind == "path":
                path = Path(value)
                if not path.is_absolute():
                    path = app_root / path
                ok = path.exists()
                results.append(
                    DependencyResult(
                        dependency,
                        ok,
                        str(path.resolve()),
                        "存在します" if ok else "見つかりません",
                    )
                )
            elif dependency.kind == "command":
                resolved = shutil.which(value)
                results.append(
                    DependencyResult(
                        dependency,
                        bool(resolved),
                        resolved or value,
                        "利用可能です" if resolved else "PATH上に見つかりません",
                    )
                )
            else:
                results.append(
                    DependencyResult(
                        dependency,
                        False,
                        value,
                        f"未対応の依存種別: {dependency.kind}",
                    )
                )
        return results

    def launch(
        self,
        manifest: AppManifest,
        app_root: Path,
        profile_id: str | None = None,
    ) -> RunningApp:
        profile = manifest.profiles[profile_id or manifest.default_profile]
        with self._lock:
            current = self._running.get(manifest.id)
            if current and current.is_running:
                return current
            if current:
                self._close_finished_streams(current)

            required_failures = [
                result
                for result in self.check_dependencies(manifest, app_root)
                if result.dependency.required and not result.ok
            ]
            if required_failures:
                details = "; ".join(
                    f"{item.dependency.label or item.dependency.value}: {item.message}"
                    for item in required_failures
                )
                raise RuntimeError(f"必要な環境を確認できません: {details}")

            running = RunningApp(manifest, profile, app_root)
            self._running[manifest.id] = running
            try:
                for step in profile.processes:
                    managed = self._start_process(manifest, step, app_root)
                    running.processes.append(managed)
            except Exception as exc:
                running.error = str(exc)
                self._terminate_running(running)
                raise

            threading.Thread(
                target=self._wait_and_open,
                args=(running,),
                name=f"ready-{manifest.id}",
                daemon=True,
            ).start()
            return running

    def _start_process(
        self, manifest: AppManifest, step: ProcessStep, app_root: Path
    ) -> ManagedProcess:
        executable = self._resolve_executable(step.executable, app_root)
        arguments = [self._expand(arg, app_root) for arg in step.arguments]
        working_directory = self._resolve_working_directory(step.working_directory, app_root)
        if not working_directory.exists():
            raise FileNotFoundError(f"作業フォルダがありません: {working_directory}")
        if any(separator in executable for separator in ("/", "\\")):
            path = Path(executable)
            if not path.exists():
                raise FileNotFoundError(f"実行ファイルがありません: {path}")

        app_log_dir = logs_dir() / manifest.id
        app_log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = app_log_dir / f"{timestamp}_{step.id}.log"
        log_stream = log_path.open("ab", buffering=0)

        environment = os.environ.copy()
        environment.update(
            {key: self._expand(value, app_root) for key, value in step.environment.items()}
        )

        command: list[str] | str
        shell = step.shell
        if shell:
            command = subprocess.list2cmdline([executable, *arguments])
        else:
            command = [executable, *arguments]

        creationflags = 0
        start_new_session = False
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            start_new_session = True

        process = subprocess.Popen(
            command,
            cwd=str(working_directory),
            env=environment,
            stdout=log_stream,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            shell=shell,
            creationflags=creationflags,
            start_new_session=start_new_session,
        )
        return ManagedProcess(step, process, log_stream)

    def _wait_and_open(self, running: RunningApp) -> None:
        try:
            for check in running.profile.ready_checks:
                if not self._wait_for_check(check.kind, check.target, check.timeout_seconds, running.app_root):
                    running.error = f"起動確認がタイムアウトしました: {check.target}"
                    self._terminate_running(running, clear_error=False)
                    return
            if running.profile.open_url:
                webbrowser.open(self._expand(running.profile.open_url, running.app_root))
            if running.profile.open_path:
                target = Path(self._expand(running.profile.open_path, running.app_root))
                if not target.is_absolute():
                    target = running.app_root / target
                self.open_path(target)
        except Exception as exc:
            running.error = str(exc)
            self._terminate_running(running, clear_error=False)

    def _wait_for_check(
        self, kind: str, target: str, timeout_seconds: float, app_root: Path
    ) -> bool:
        target = self._expand(target, app_root)
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if kind == "http":
                try:
                    with urllib.request.urlopen(target, timeout=1.5) as response:
                        if 200 <= response.status < 500:
                            return True
                except (urllib.error.URLError, TimeoutError, ValueError):
                    pass
            elif kind == "tcp":
                host, port_text = target.rsplit(":", 1)
                try:
                    with socket.create_connection((host, int(port_text)), timeout=1.0):
                        return True
                except OSError:
                    pass
            elif kind == "path":
                path = Path(target)
                if not path.is_absolute():
                    path = app_root / path
                if path.exists():
                    return True
            time.sleep(0.35)
        return False

    def status(self, app_id: str) -> str:
        with self._lock:
            running = self._running.get(app_id)
            if not running:
                return "stopped"
            if running.error:
                return "error"
            if running.is_running:
                return "running"
            self._close_finished_streams(running)
            return "stopped"

    def error(self, app_id: str) -> str | None:
        with self._lock:
            running = self._running.get(app_id)
            return running.error if running else None

    def stop(self, app_id: str) -> None:
        with self._lock:
            running = self._running.get(app_id)
            if not running:
                return
            self._terminate_running(running)

    def restart(self, manifest: AppManifest, app_root: Path) -> RunningApp:
        self.stop(manifest.id)
        return self.launch(manifest, app_root)

    def _close_finished_streams(self, running: RunningApp) -> None:
        for managed in running.processes:
            if managed.process.poll() is not None and not managed.log_stream.closed:
                try:
                    managed.log_stream.close()
                except OSError:
                    pass

    def _terminate_running(
        self, running: RunningApp, clear_error: bool = True
    ) -> None:
        for managed in reversed(running.processes):
            process = managed.process
            if process.poll() is not None:
                managed.log_stream.close()
                continue
            try:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            finally:
                try:
                    managed.log_stream.close()
                except OSError:
                    pass
        running.processes.clear()
        if clear_error:
            running.error = None

    def open_logs(self, app_id: str) -> None:
        path = logs_dir() / app_id
        path.mkdir(parents=True, exist_ok=True)
        self.open_path(path)

    @staticmethod
    def open_path(path: Path) -> None:
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", str(path)])
        elif shutil.which("open"):
            subprocess.Popen(["open", str(path)])
        else:
            raise RuntimeError("フォルダを開くコマンドが見つかりません")
