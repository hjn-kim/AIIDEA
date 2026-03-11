COLORS = {
    # ── 사이드바 (다크, AIIDEA 로고 흰색)
    "sidebar_bg":     "#252530",
    "sidebar_hover":  "#353545",
    "sidebar_active": "#3A3A4A",
    "sidebar_text":   "#FFFFFF",
    "sidebar_muted":  "#B0B0C0",
    "sidebar_border": "#3A3A50",

    # ── 콘텐츠 (다크)
    "bg_main":        "#171717",
    "bg_panel":       "#212121",
    "bg_input":       "#2A2A2A",
    "bg_hover":       "#333333",

    # ── 텍스트
    "text_primary":   "#ECECEC",
    "text_secondary": "#8E8EA0",
    "text_muted":     "#6E6E80",

    # ── 강조색
    "accent_green":   "#0D3B5E",
    "accent_hover":   "#0D3B5E",
    "accent_blue":    "#0D3B5E",
    "accent_blue_h":  "#0D3B5E",

    # ── 테두리 / 기타
    "border":         "#3A3A3A",
    "border_focus":   "#0D3B5E",
    "danger":         "#EF4444",
    "danger_light":   "#2D1111",
    "warning":        "#F59E0B",
    "success":        "#0D3B5E",
}

MAIN_STYLESHEET = f"""
/* ══════════════════════════════════════════
   베이스
══════════════════════════════════════════ */
QMainWindow, QWidget {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_primary']};
    font-family: 'Malgun Gothic', 'Segoe UI', sans-serif;
    font-size: 10pt;
}}

QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: {COLORS['bg_main']};
    border: none;
}}

/* ══════════════════════════════════════════
   사이드바
══════════════════════════════════════════ */
QWidget#sidebar {{
    background-color: {COLORS['sidebar_bg']};
}}

QLabel#sidebarLogo {{
    color: #FFFFFF;
    font-size: 18pt;
    font-weight: bold;
    padding: 22px 16px 18px 20px;
    margin-left: 10px;
}}

/* 네비게이션 버튼 */
QPushButton#navButton {{
    background-color: transparent;
    color: {COLORS['sidebar_muted']};
    border: none;
    border-radius: 8px;
    padding: 11px 14px;
    text-align: left;
    font-size: 10pt;
    font-weight: normal;
    margin: 1px 8px;
}}
QPushButton#navButton:hover {{
    background-color: {COLORS['sidebar_hover']};
    color: {COLORS['sidebar_text']};
}}
QPushButton#navButton:checked {{
    background-color: {COLORS['sidebar_active']};
    color: {COLORS['sidebar_text']};
    font-weight: bold;
}}

/* 설정 버튼 */
QPushButton#settingsButton {{
    background-color: black;
    color: #D0D0E0;
    border: 1px solid black;
    border-radius: 8px;
    padding: 4px 12px;
    margin: 8px 10px 10px 10px;
    text-align: left;
    font-size: 9pt;
    font-weight: normal;
    min-height: 36px;
}}
QPushButton#settingsButton:hover {{
    background-color: #3A3A52;
    color: #FFFFFF;
    border-color: #6A6A80;
}}
QPushButton#settingsButton:pressed {{
    background-color: #252535;
    color: #FFFFFF;
}}

/* ══════════════════════════════════════════
   콘텐츠 영역
══════════════════════════════════════════ */
QWidget#contentArea {{
    background-color: {COLORS['bg_main']};
}}

QLabel#pageTitle {{
    font-size: 15pt;
    font-weight: bold;
    color: {COLORS['text_primary']};
    padding: 0px 0px 2px 0px;
}}

QLabel#sectionLabel {{
    color: {COLORS['text_secondary']};
    font-size: 8pt;
    font-weight: bold;
    padding: 2px 0px 2px 0px;
}}

/* ══════════════════════════════════════════
   입력 필드
══════════════════════════════════════════ */
QLineEdit, QDateEdit {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 9px 12px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_green']};
}}
QLineEdit:hover, QDateEdit:hover {{
    border-color: #555555;
}}
QLineEdit:focus, QDateEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
}}

QTextEdit {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 12px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_green']};
}}
QTextEdit:hover {{
    border-color: #555555;
}}
QTextEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
}}

/* ══════════════════════════════════════════
   콤보박스
══════════════════════════════════════════ */
QComboBox {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
    min-width: 140px;
}}
QComboBox:hover {{
    border-color: #555555;
}}
QComboBox:focus {{
    border: 2px solid {COLORS['border_focus']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
    padding-right: 4px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    selection-background-color: {COLORS['accent_green']};
    selection-color: white;
    color: {COLORS['text_primary']};
    padding: 4px;
}}
QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    border-radius: 4px;
    min-height: 28px;
}}

/* 테이블 셀 안 콤보박스: min-width 강제 해제 */
QTableWidget QComboBox {{
    min-width: 0px;
    padding: 4px 8px;
    border-radius: 4px;
}}

/* ══════════════════════════════════════════
   버튼
══════════════════════════════════════════ */
QPushButton {{
    background-color: #404040;
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: bold;
    font-size: 10pt;
}}
QPushButton:hover {{
    background-color: #505050;
    border-color: #606060;
}}
QPushButton:pressed {{
    background-color: #353535;
}}
QPushButton:disabled {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text_muted']};
    border: 1px solid {COLORS['border']};
}}

/* AI 버튼 (ChatGPT 그린) */
QPushButton#aiButton {{
    background-color: {COLORS['accent_green']};
    color: white;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: bold;
}}
QPushButton#aiButton:hover {{
    background-color: {COLORS['accent_hover']};
}}
QPushButton#aiButton:disabled {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text_muted']};
    border: 1px solid {COLORS['border']};
}}

/* 위험 버튼 */
QPushButton#dangerButton {{
    background-color: transparent;
    color: {COLORS['danger']};
    border: 1px solid #7F1D1D;
    border-radius: 8px;
}}
QPushButton#dangerButton:hover {{
    background-color: {COLORS['danger_light']};
    border-color: {COLORS['danger']};
}}

/* 보조 버튼 */
QPushButton#secondaryButton {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
}}
QPushButton#secondaryButton:hover {{
    background-color: {COLORS['bg_panel']};
    border-color: #555555;
}}

/* ══════════════════════════════════════════
   테이블
══════════════════════════════════════════ */
QTableWidget {{
    background-color: {COLORS['bg_main']};
    gridline-color: {COLORS['border']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    selection-background-color: #0D3B5E;
    selection-color: {COLORS['text_primary']};
}}
QTableWidget::item {{
    padding: 10px 12px;
    border: none;
    color: {COLORS['text_primary']};
}}
QTableWidget::item:selected {{
    background-color: #0D3B5E;
    color: {COLORS['text_primary']};
}}
QTableWidget::item:hover {{
    background-color: {COLORS['bg_panel']};
}}
QHeaderView {{
    background-color: {COLORS['bg_main']};
}}
QHeaderView::section {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text_secondary']};
    padding: 10px 12px;
    border: none;
    border-right: 1px solid {COLORS['border']};
    border-bottom: 1px solid {COLORS['border']};
    font-weight: bold;
    font-size: 8pt;
}}
QHeaderView::section:first {{
    border-top-left-radius: 10px;
}}

/* ══════════════════════════════════════════
   탭
══════════════════════════════════════════ */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['bg_main']};
    border-radius: 0px 10px 10px 10px;
}}
QTabBar {{
    background-color: transparent;
}}
QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    padding: 10px 18px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 10pt;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    color: {COLORS['text_primary']};
    border-bottom: 2px solid {COLORS['accent_green']};
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    color: {COLORS['text_primary']};
    background-color: {COLORS['bg_panel']};
    border-radius: 6px 6px 0px 0px;
}}

/* ══════════════════════════════════════════
   스크롤바
══════════════════════════════════════════ */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: #555555;
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: #888888;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
}}
QScrollBar::handle:horizontal {{
    background: #555555;
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: #888888;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ══════════════════════════════════════════
   상태바
══════════════════════════════════════════ */
QStatusBar {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border']};
    font-size: 8pt;
    padding: 0px 12px;
}}

/* ══════════════════════════════════════════
   다이얼로그
══════════════════════════════════════════ */
QDialog {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_primary']};
}}
QMessageBox {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_primary']};
}}
QMessageBox QPushButton {{
    min-width: 80px;
    min-height: 32px;
}}

/* ══════════════════════════════════════════
   메뉴
══════════════════════════════════════════ */
QMenu {{
    background-color: {COLORS['bg_main']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 6px;
    color: {COLORS['text_primary']};
}}
QMenu::item {{
    padding: 9px 16px;
    border-radius: 6px;
    font-size: 10pt;
}}
QMenu::item:selected {{
    background-color: {COLORS['bg_panel']};
    color: {COLORS['text_primary']};
}}

/* ══════════════════════════════════════════
   구분선
══════════════════════════════════════════ */
QFrame[frameShape="4"], QFrame[frameShape="HLine"] {{
    color: {COLORS['border']};
    border: none;
    border-top: 1px solid {COLORS['border']};
    max-height: 1px;
}}

/* ══════════════════════════════════════════
   스핀박스
══════════════════════════════════════════ */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
}}
QSpinBox:hover, QDoubleSpinBox:hover {{
    border-color: #555555;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {COLORS['border_focus']};
}}
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    border: none;
    background: transparent;
    width: 16px;
}}

/* ══════════════════════════════════════════
   리스트 위젯
══════════════════════════════════════════ */
QListWidget {{
    background-color: {COLORS['bg_panel']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 4px;
    color: {COLORS['text_primary']};
}}
QListWidget::item {{
    padding: 10px 12px;
    border-radius: 6px;
    color: {COLORS['text_primary']};
}}
QListWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
}}
QListWidget::item:selected {{
    background-color: #0D3B5E;
    color: {COLORS['text_primary']};
    font-weight: bold;
}}

/* ══════════════════════════════════════════
   그룹박스
══════════════════════════════════════════ */
QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    margin-top: 10px;
    padding: 16px 12px 12px 12px;
    font-weight: bold;
    color: {COLORS['text_secondary']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: {COLORS['text_secondary']};
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_secondary']};
}}

/* ══════════════════════════════════════════
   프로그레스바
══════════════════════════════════════════ */
QProgressBar {{
    background-color: {COLORS['bg_panel']};
    border: none;
    border-radius: 2px;
}}
QProgressBar::chunk {{
    background-color: {COLORS['accent_green']};
    border-radius: 2px;
}}

/* ══════════════════════════════════════════
   분리자 (QSplitter)
══════════════════════════════════════════ */
QSplitter::handle {{
    background-color: {COLORS['border']};
    width: 1px;
}}
QSplitter::handle:hover {{
    background-color: {COLORS['accent_green']};
}}
"""
