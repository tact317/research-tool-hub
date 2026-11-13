APP_STYLE = r"""
QWidget {
    background: #09090b;
    color: #e4e4e7;
    font-family: "Yu Gothic UI", "Noto Sans JP", "Segoe UI";
    font-size: 13px;
}
QMainWindow { background: #09090b; }
QFrame#Sidebar {
    background: #0c0c0f;
    border-right: 1px solid #242429;
}
QLabel#Brand { font-size: 18px; font-weight: 700; color: #fafafa; }
QLabel#Muted { color: #8b8b95; }
QLabel#PageTitle { font-size: 24px; font-weight: 700; color: #fafafa; }
QLineEdit {
    background: #121216;
    border: 1px solid #29292f;
    border-radius: 8px;
    padding: 9px 12px;
    selection-background-color: #3f3f46;
}
QLineEdit:focus { border: 1px solid #52525b; }
QPushButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 7px;
    padding: 8px 10px;
    text-align: left;
}
QPushButton:hover { background: #18181d; }
QPushButton:pressed { background: #222228; }
QPushButton#PrimaryButton {
    background: #f4f4f5;
    color: #18181b;
    font-weight: 650;
    text-align: center;
    padding: 8px 15px;
}
QPushButton#PrimaryButton:hover { background: #d4d4d8; }
QPushButton#DangerButton {
    background: #281416;
    border: 1px solid #4b2025;
    color: #fda4af;
    text-align: center;
}
QPushButton#SecondaryButton {
    background: #16161b;
    border: 1px solid #2b2b32;
    text-align: center;
}
QFrame#AppCard {
    background: #101014;
    border: 1px solid #26262c;
    border-radius: 12px;
}
QFrame#AppCard:hover { border: 1px solid #3a3a42; }
QLabel#AppTitle { font-size: 15px; font-weight: 650; color: #fafafa; }
QLabel#StatusRunning { color: #86efac; }
QLabel#StatusStopped { color: #a1a1aa; }
QLabel#StatusError { color: #fda4af; }
QLabel#Tag {
    background: #1b1b20;
    color: #a1a1aa;
    border: 1px solid #292930;
    border-radius: 5px;
    padding: 2px 6px;
}
QScrollArea { border: none; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 3px; }
QScrollBar::handle:vertical { background: #303038; min-height: 30px; border-radius: 4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QDialog { background: #0d0d11; }
QTextEdit {
    background: #0a0a0d;
    border: 1px solid #29292f;
    border-radius: 8px;
    padding: 8px;
    font-family: "Cascadia Mono", Consolas, monospace;
}
QComboBox {
    background: #15151a;
    border: 1px solid #2c2c32;
    border-radius: 7px;
    padding: 7px 10px;
}
QToolTip { background: #18181b; color: #fafafa; border: 1px solid #3f3f46; }
"""
