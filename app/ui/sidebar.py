from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt6.QtCore import pyqtSignal, Qt


class SidebarWidget(QWidget):
    page_changed = pyqtSignal(int)
    settings_clicked = pyqtSignal()

    # 순서: 0.보고서, 1.제안서, 2.수익성분석, 3.회의록, 4.DB자료저장, 5.오류&개선사항, 6.사용설명서
    NAV_ITEMS = [
        ("📊", "보고서",       0),
        ("📄", "제안서",       1),
        ("💹", "수익성 분석",  2),
        ("📋", "회의록",       3),
        ("🗄",  "DB 자료 저장", 4),
        ("💬", "오류 및 개선방안",  5),
        ("📖", "사용설명서",   6),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 로고
        logo = QLabel("AIIDEA")
        logo.setObjectName("sidebarLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(logo)

        # 구분선
        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #3A3A50;")
        layout.addWidget(line)
        layout.addSpacing(8)

        # 네비게이션 버튼
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self._nav_buttons = []

        for icon, label, index in self.NAV_ITEMS:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda _, i=index: self.page_changed.emit(i))
            self.btn_group.addButton(btn, index)
            self._nav_buttons.append(btn)
            layout.addWidget(btn)

        # 첫 번째 버튼 기본 선택
        if self._nav_buttons:
            self._nav_buttons[0].setChecked(True)

        layout.addStretch()

        # 구분선
        line2 = QLabel()
        line2.setFixedHeight(1)
        line2.setStyleSheet("background-color: #3A3A50;")
        layout.addWidget(line2)

        layout.addSpacing(12)

        # 설정 버튼
        settings_btn = QPushButton("API key")
        settings_btn.setObjectName("settingsButton")
        settings_btn.setMinimumHeight(25)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(settings_btn)
        layout.addSpacing(12)

    def set_active_page(self, index: int):
        if 0 <= index < len(self._nav_buttons):
            self._nav_buttons[index].setChecked(True)
