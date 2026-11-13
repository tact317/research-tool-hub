from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from research_tool_hub.models import AppManifest


class AppCard(QFrame):
    launch_requested = Signal(str)
    stop_requested = Signal(str)
    details_requested = Signal(str)
    favorite_requested = Signal(str)
    root_requested = Signal(str)

    def __init__(self, manifest: AppManifest, root_exists: bool, favorite: bool) -> None:
        super().__init__()
        self.manifest = manifest
        self.setObjectName("AppCard")
        self.setMinimumWidth(300)
        self.setMaximumWidth(430)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 15, 16, 14)
        outer.setSpacing(10)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel(manifest.name)
        title.setObjectName("AppTitle")
        subtitle = QLabel(
            f"{manifest.category}  ·  {manifest.version or 'version unknown'}"
        )
        subtitle.setObjectName("Muted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)
        self.favorite_button = QPushButton("★" if favorite else "☆")
        self.favorite_button.setFixedWidth(38)
        self.favorite_button.setToolTip("お気に入り")
        self.favorite_button.clicked.connect(
            lambda: self.favorite_requested.emit(manifest.id)
        )
        header.addWidget(self.favorite_button)
        outer.addLayout(header)

        description = QLabel(manifest.description or "説明は登録されていません。")
        description.setObjectName("Muted")
        description.setWordWrap(True)
        description.setMinimumHeight(38)
        outer.addWidget(description)

        tags_row = QHBoxLayout()
        tags_row.setSpacing(5)
        tags = manifest.tags[:3] or [manifest.category]
        for text in tags:
            label = QLabel(text)
            label.setObjectName("Tag")
            tags_row.addWidget(label)
        tags_row.addStretch(1)
        outer.addLayout(tags_row)

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background:#26262c;")
        outer.addWidget(separator)

        footer = QHBoxLayout()
        self.status_label = QLabel("停止中")
        self.status_label.setObjectName("StatusStopped")
        footer.addWidget(self.status_label, 1)

        self.root_button = QPushButton("場所を設定")
        self.root_button.setObjectName("SecondaryButton")
        self.root_button.clicked.connect(lambda: self.root_requested.emit(manifest.id))
        self.root_button.setVisible(not root_exists)
        footer.addWidget(self.root_button)

        details = QPushButton("詳細")
        details.setObjectName("SecondaryButton")
        details.clicked.connect(lambda: self.details_requested.emit(manifest.id))
        footer.addWidget(details)

        self.action_button = QPushButton("起動")
        self.action_button.setObjectName("PrimaryButton")
        self.action_button.clicked.connect(self._action_clicked)
        footer.addWidget(self.action_button)
        outer.addLayout(footer)

    def _action_clicked(self) -> None:
        if self.action_button.text() == "停止":
            self.stop_requested.emit(self.manifest.id)
        else:
            self.launch_requested.emit(self.manifest.id)

    def set_status(self, status: str, error: str | None = None) -> None:
        if status == "running":
            self.status_label.setText("● 実行中")
            self.status_label.setObjectName("StatusRunning")
            self.action_button.setText("停止")
            self.action_button.setObjectName("DangerButton")
        elif status == "error":
            self.status_label.setText("● 起動エラー")
            self.status_label.setToolTip(error or "")
            self.status_label.setObjectName("StatusError")
            self.action_button.setText("再試行")
            self.action_button.setObjectName("PrimaryButton")
        else:
            self.status_label.setText("停止中")
            self.status_label.setToolTip("")
            self.status_label.setObjectName("StatusStopped")
            self.action_button.setText("起動")
            self.action_button.setObjectName("PrimaryButton")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.action_button.style().unpolish(self.action_button)
        self.action_button.style().polish(self.action_button)

    def set_root_exists(self, exists: bool) -> None:
        self.root_button.setVisible(not exists)
