from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from research_tool_hub.models import AppManifest
from research_tool_hub.process_manager import DependencyResult


class AppDetailsDialog(QDialog):
    def __init__(
        self,
        manifest: AppManifest,
        app_root: Path,
        dependencies: list[DependencyResult],
        open_folder,
        open_logs,
        open_documentation,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{manifest.name} - 詳細")
        self.resize(700, 560)
        layout = QVBoxLayout(self)

        title = QLabel(f"<b>{manifest.name}</b>  {manifest.version}")
        title.setStyleSheet("font-size:18px;")
        layout.addWidget(title)
        layout.addWidget(QLabel(manifest.description))
        layout.addWidget(QLabel(f"カテゴリ: {manifest.category}"))
        layout.addWidget(QLabel(f"アプリ配置先: {app_root}"))

        dependency_lines = []
        if dependencies:
            for result in dependencies:
                mark = "OK" if result.ok else "NG"
                requirement = "必須" if result.dependency.required else "任意"
                dependency_lines.append(
                    f"[{mark}] {result.dependency.label or result.dependency.value}"
                    f" ({requirement}) - {result.message}\n    {result.resolved}"
                )
        else:
            dependency_lines.append("依存環境の定義はありません。")
        dependency_view = QTextEdit()
        dependency_view.setReadOnly(True)
        dependency_view.setPlainText("\n".join(dependency_lines))
        dependency_view.setMaximumHeight(150)
        layout.addWidget(QLabel("依存環境"))
        layout.addWidget(dependency_view)

        raw_view = QTextEdit()
        raw_view.setReadOnly(True)
        try:
            parsed = json.loads(manifest.source_path.read_text(encoding="utf-8-sig"))
            raw_view.setPlainText(json.dumps(parsed, ensure_ascii=False, indent=2))
        except Exception:
            raw_view.setPlainText(str(manifest.source_path))
        layout.addWidget(QLabel("マニフェスト"))
        layout.addWidget(raw_view, 1)

        actions = QHBoxLayout()
        folder_button = QPushButton("アプリフォルダ")
        folder_button.setObjectName("SecondaryButton")
        folder_button.clicked.connect(open_folder)
        actions.addWidget(folder_button)
        log_button = QPushButton("ログ")
        log_button.setObjectName("SecondaryButton")
        log_button.clicked.connect(open_logs)
        actions.addWidget(log_button)
        if manifest.documentation:
            doc_button = QPushButton("README")
            doc_button.setObjectName("SecondaryButton")
            doc_button.clicked.connect(open_documentation)
            actions.addWidget(doc_button)
        actions.addStretch(1)
        layout.addLayout(actions)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
