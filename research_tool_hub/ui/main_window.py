from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from research_tool_hub.manifest_loader import discover_manifests
from research_tool_hub.models import AppManifest
from research_tool_hub.paths import manifests_dir
from research_tool_hub.process_manager import ProcessManager
from research_tool_hub.storage import AppStateStore
from research_tool_hub.ui.dialogs import AppDetailsDialog
from research_tool_hub.ui.theme import APP_STYLE
from research_tool_hub.ui.widgets import AppCard


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Research Tool Hub")
        self.resize(1280, 780)
        self.setMinimumSize(980, 640)

        self.process_manager = ProcessManager()
        self.state_store = AppStateStore()
        self.apps: dict[str, AppManifest] = {}
        self.cards: dict[str, AppCard] = {}
        self.selected_category = "すべて"
        self.selected_view = "all"

        self._build_ui()
        self.reload_manifests()

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_statuses)
        self.status_timer.start(900)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(232)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 20, 14, 18)
        sidebar_layout.setSpacing(5)

        brand = QLabel("Research Tool Hub")
        brand.setObjectName("Brand")
        sidebar_layout.addWidget(brand)
        version = QLabel("研究・開発アプリ統合ランチャー  v0.1")
        version.setObjectName("Muted")
        version.setWordWrap(True)
        sidebar_layout.addWidget(version)
        sidebar_layout.addSpacing(20)

        self.home_button = self._nav_button("すべてのツール", lambda: self._set_view("all"))
        self.favorite_button = self._nav_button("お気に入り", lambda: self._set_view("favorites"))
        self.recent_button = self._nav_button("最近使用", lambda: self._set_view("recent"))
        sidebar_layout.addWidget(self.home_button)
        sidebar_layout.addWidget(self.favorite_button)
        sidebar_layout.addWidget(self.recent_button)
        sidebar_layout.addSpacing(18)

        category_label = QLabel("カテゴリ")
        category_label.setObjectName("Muted")
        sidebar_layout.addWidget(category_label)
        self.category_container = QVBoxLayout()
        self.category_container.setSpacing(3)
        sidebar_layout.addLayout(self.category_container)
        sidebar_layout.addStretch(1)

        add_button = QPushButton("＋ マニフェストを追加")
        add_button.setObjectName("SecondaryButton")
        add_button.clicked.connect(self.import_manifest)
        sidebar_layout.addWidget(add_button)

        reload_button = QPushButton("一覧を再読み込み")
        reload_button.clicked.connect(self.reload_manifests)
        sidebar_layout.addWidget(reload_button)

        root.addWidget(sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 20)
        content_layout.setSpacing(18)

        top = QHBoxLayout()
        title_box = QVBoxLayout()
        self.page_title = QLabel("すべてのツール")
        self.page_title.setObjectName("PageTitle")
        self.summary_label = QLabel("")
        self.summary_label.setObjectName("Muted")
        title_box.addWidget(self.page_title)
        title_box.addWidget(self.summary_label)
        top.addLayout(title_box, 1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("アプリ名・説明・タグを検索")
        self.search.setClearButtonEnabled(True)
        self.search.setFixedWidth(340)
        self.search.textChanged.connect(self.render_cards)
        top.addWidget(self.search)
        content_layout.addLayout(top)

        self.notice = QLabel("")
        self.notice.setObjectName("Muted")
        self.notice.setWordWrap(True)
        self.notice.hide()
        content_layout.addWidget(self.notice)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.card_host = QWidget()
        self.grid = QGridLayout(self.card_host)
        self.grid.setContentsMargins(0, 0, 6, 8)
        self.grid.setHorizontalSpacing(14)
        self.grid.setVerticalSpacing(14)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.card_host)
        content_layout.addWidget(scroll, 1)

        root.addWidget(content, 1)

    def _nav_button(self, text: str, callback) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button

    def reload_manifests(self) -> None:
        manifests, issues = discover_manifests(manifests_dir())
        self.apps = {manifest.id: manifest for manifest in manifests}
        if issues:
            self.notice.setText(
                "一部のマニフェストを読み込めませんでした:\n"
                + "\n".join(f"・{issue.path.name}: {issue.message}" for issue in issues)
            )
            self.notice.show()
        else:
            self.notice.hide()
        self._rebuild_categories()
        self.render_cards()

    def _rebuild_categories(self) -> None:
        while self.category_container.count():
            item = self.category_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for category in sorted({app.category for app in self.apps.values()}):
            button = QPushButton(category)
            button.clicked.connect(lambda checked=False, value=category: self._set_category(value))
            self.category_container.addWidget(button)

    def _set_view(self, view: str) -> None:
        self.selected_view = view
        self.selected_category = "すべて"
        titles = {"all": "すべてのツール", "favorites": "お気に入り", "recent": "最近使用"}
        self.page_title.setText(titles[view])
        self.render_cards()

    def _set_category(self, category: str) -> None:
        self.selected_view = "all"
        self.selected_category = category
        self.page_title.setText(category)
        self.render_cards()

    def _app_root(self, app: AppManifest) -> Path:
        override = self.state_store.app_roots().get(app.id)
        return self.process_manager.resolve_app_root(app, override)

    def _filtered_apps(self) -> list[AppManifest]:
        apps = list(self.apps.values())
        if self.selected_view == "favorites":
            favorites = self.state_store.favorites()
            apps = [app for app in apps if app.id in favorites]
        elif self.selected_view == "recent":
            order = self.state_store.recent()
            by_id = {app.id: app for app in apps}
            apps = [by_id[app_id] for app_id in order if app_id in by_id]
        elif self.selected_category != "すべて":
            apps = [app for app in apps if app.category == self.selected_category]

        query = self.search.text().strip().lower()
        if query:
            apps = [
                app
                for app in apps
                if query
                in " ".join(
                    [app.name, app.description, app.category, app.version, *app.tags]
                ).lower()
            ]
        if self.selected_view != "recent":
            apps.sort(key=lambda app: (app.category, app.name.lower()))
        return apps

    def render_cards(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.cards.clear()

        apps = self._filtered_apps()
        favorites = self.state_store.favorites()
        columns = 3 if self.width() >= 1230 else 2
        for index, app in enumerate(apps):
            root_exists = self._app_root(app).exists()
            card = AppCard(app, root_exists, app.id in favorites)
            card.launch_requested.connect(self.launch_app)
            card.stop_requested.connect(self.stop_app)
            card.details_requested.connect(self.show_details)
            card.favorite_requested.connect(self.toggle_favorite)
            card.root_requested.connect(self.choose_app_root)
            self.grid.addWidget(card, index // columns, index % columns)
            self.cards[app.id] = card
        self.summary_label.setText(f"{len(apps)} 件表示 / 登録 {len(self.apps)} 件")
        self.refresh_statuses()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.apps:
            QTimer.singleShot(0, self.render_cards)

    def launch_app(self, app_id: str) -> None:
        app = self.apps[app_id]
        root = self._app_root(app)
        if not root.exists():
            self.choose_app_root(app_id)
            root = self._app_root(app)
            if not root.exists():
                return
        try:
            self.process_manager.launch(app, root)
            self.state_store.mark_recent(app_id)
            self.refresh_statuses()
        except Exception as exc:
            QMessageBox.critical(self, "起動できません", str(exc))

    def stop_app(self, app_id: str) -> None:
        self.process_manager.stop(app_id)
        self.refresh_statuses()

    def choose_app_root(self, app_id: str) -> None:
        app = self.apps[app_id]
        selected = QFileDialog.getExistingDirectory(
            self,
            f"{app.name} のルートフォルダを選択",
            str(self._app_root(app).parent),
        )
        if not selected:
            return
        self.state_store.set_app_root(app_id, Path(selected))
        card = self.cards.get(app_id)
        if card:
            card.set_root_exists(True)

    def toggle_favorite(self, app_id: str) -> None:
        self.state_store.toggle_favorite(app_id)
        self.render_cards()

    def show_details(self, app_id: str) -> None:
        app = self.apps[app_id]
        root = self._app_root(app)
        dependencies = self.process_manager.check_dependencies(app, root)

        def open_folder() -> None:
            if root.exists():
                self.process_manager.open_path(root)
            else:
                QMessageBox.warning(self, "フォルダなし", str(root))

        def open_documentation() -> None:
            if not app.documentation:
                return
            target = Path(app.documentation)
            if not target.is_absolute():
                target = root / target
            if target.exists():
                self.process_manager.open_path(target)
            else:
                QMessageBox.warning(self, "READMEなし", str(target))

        dialog = AppDetailsDialog(
            app,
            root,
            dependencies,
            open_folder,
            lambda: self.process_manager.open_logs(app_id),
            open_documentation,
            self,
        )
        dialog.exec()

    def refresh_statuses(self) -> None:
        for app_id, card in self.cards.items():
            card.set_status(
                self.process_manager.status(app_id), self.process_manager.error(app_id)
            )

    def import_manifest(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, "マニフェストを追加", "", "JSON (*.json)"
        )
        if not selected:
            return
        source = Path(selected)
        destination = manifests_dir() / source.name
        if destination.exists():
            answer = QMessageBox.question(
                self,
                "上書き確認",
                f"{destination.name} は既にあります。上書きしますか？",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        shutil.copy2(source, destination)
        self.reload_manifests()

    def closeEvent(self, event: QCloseEvent) -> None:
        running_ids = [app_id for app_id in self.apps if self.process_manager.status(app_id) == "running"]
        if running_ids:
            answer = QMessageBox.question(
                self,
                "実行中のアプリ",
                "統合ランチャーが起動したプロセスも終了しますか？",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            if answer == QMessageBox.StandardButton.Yes:
                for app_id in running_ids:
                    self.process_manager.stop(app_id)
        event.accept()


def run_app() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Research Tool Hub")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    return app.exec()
