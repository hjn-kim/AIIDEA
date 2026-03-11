from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from app.ui.sidebar import SidebarWidget
from app.modules.meeting_minutes.view import MeetingMinutesWidget
from app.modules.proposal.view import ProposalWidget
from app.modules.report.view import ReportWidget
from app.modules.profitability.view import ProfitabilityWidget
from app.modules.db.view import DBWidget
from app.modules.feedback.view import FeedbackWidget
from app.modules.manual.view import ManualWidget


class SettingsDialog(QDialog):
    def __init__(self, current_key: str = "", current_name: str = "",
                 parent=None, first_run: bool = False):
        super().__init__(parent)
        self.first_run = first_run
        self.setWindowTitle("초기 설정" if first_run else "설정 / API 키 관리")
        self.setMinimumWidth(480)
        self.setModal(True)
        if first_run:
            self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("초기 설정" if first_run else "설정")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        desc_text = (
            "처음 실행되었습니다. 이름과 Gemini API 키를 입력하세요.\n"
            "입력 정보는 앱 폴더의 .env 파일에 저장됩니다."
        ) if first_run else (
            "사용자 이름 및 Gemini API 키를 관리합니다.\n"
            "변경 후 저장하면 즉시 적용됩니다."
        )
        desc = QLabel(desc_text)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9090A8; font-size: 9pt;")
        layout.addWidget(desc)

        # 이름 입력
        name_lbl = QLabel("이름")
        name_lbl.setStyleSheet("font-size: 9pt; font-weight: bold;")
        layout.addWidget(name_lbl)
        self.name_input = QLineEdit(current_name)
        self.name_input.setPlaceholderText("성함을 입력해주세요")
        layout.addWidget(self.name_input)

        # API 키 입력
        key_lbl = QLabel("Gemini API 키")
        key_lbl.setStyleSheet("font-size: 9pt; font-weight: bold;")
        layout.addWidget(key_lbl)
        self.key_input = QLineEdit(current_key)
        self.key_input.setPlaceholderText("AIza...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.key_input)

        show_btn = QPushButton("Key 보기 / 숨기기")
        show_btn.setObjectName("secondaryButton")
        show_btn.clicked.connect(self._toggle_echo)
        layout.addWidget(show_btn)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _toggle_echo(self):
        if self.key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)

    def _save(self):
        name = self.name_input.text().strip()
        key = self.key_input.text().strip()
        if self.first_run and not name:
            QMessageBox.warning(self, "경고", "이름을 입력하세요.")
            return
        if not key:
            QMessageBox.warning(self, "경고", "API 키를 입력하세요.")
            return
        self.accept()

    def get_key(self) -> str:
        return self.key_input.text().strip()

    def get_name(self) -> str:
        return self.name_input.text().strip()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AIIDEA")
        self.setMinimumSize(1280, 800)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 사이드바
        self.sidebar = SidebarWidget()
        self.sidebar.page_changed.connect(self._switch_page)
        self.sidebar.settings_clicked.connect(self._open_settings)
        root_layout.addWidget(self.sidebar)

        # 콘텐츠 스택
        self.stack = QStackedWidget()
        self.stack.setObjectName("contentArea")

        self.report_widget = ReportWidget()
        self.proposal_widget = ProposalWidget()
        self.profitability_widget = ProfitabilityWidget()
        self.meeting_widget = MeetingMinutesWidget()
        self.db_widget = DBWidget()
        self.feedback_widget = FeedbackWidget()
        self.manual_widget = ManualWidget()

        self.stack.addWidget(self.report_widget)        # index 0 보고서
        self.stack.addWidget(self.proposal_widget)      # index 1 제안서
        self.stack.addWidget(self.profitability_widget) # index 2 수익성 분석
        self.stack.addWidget(self.meeting_widget)       # index 3 회의록
        self.stack.addWidget(self.db_widget)            # index 4 DB 자료 저장
        self.stack.addWidget(self.feedback_widget)      # index 5 오류 & 개선사항
        self.stack.addWidget(self.manual_widget)        # index 6 사용설명서

        root_layout.addWidget(self.stack)

        # 상태바
        self.statusBar().showMessage("준비됨")

        # 상태 공유 (모든 모듈이 상태바에 메시지 표시 가능)
        for w in [self.report_widget, self.proposal_widget,
                  self.profitability_widget, self.meeting_widget,
                  self.db_widget, self.feedback_widget, self.manual_widget]:
            if hasattr(w, 'status_message'):
                w.status_message.connect(self.statusBar().showMessage)

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        titles = ["보고서", "제안서", "수익성 분석", "회의록", "DB 자료 저장", "오류 & 개선사항", "사용설명서"]
        self.statusBar().showMessage(f"{titles[index]} 모드")

    def _open_settings(self, first_run: bool = False):
        import os
        current_key = os.environ.get("GEMINI_API_KEY", "")
        current_name = os.environ.get("USER_NAME", "")
        dialog = SettingsDialog(current_key, current_name, self, first_run=first_run)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_env(dialog.get_key(), dialog.get_name())

    def _save_env(self, key: str, name: str):
        import sys, os
        from pathlib import Path
        from app.ai_client import GeminiClient

        if getattr(sys, 'frozen', False):
            env_path = Path(sys.executable).parent / ".env"
        else:
            env_path = Path(__file__).parent.parent.parent / ".env"

        os.environ["GEMINI_API_KEY"] = key
        os.environ["USER_NAME"] = name

        # .env 파일 읽어서 해당 키만 교체, 없으면 추가
        lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
        updated = {"GEMINI_API_KEY": False, "USER_NAME": False}
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={key}")
                updated["GEMINI_API_KEY"] = True
            elif line.startswith("USER_NAME="):
                new_lines.append(f"USER_NAME={name}")
                updated["USER_NAME"] = True
            else:
                new_lines.append(line)
        if not updated["GEMINI_API_KEY"]:
            new_lines.append(f"GEMINI_API_KEY={key}")
        if not updated["USER_NAME"]:
            new_lines.append(f"USER_NAME={name}")
        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

        GeminiClient.reset_instance()
        QMessageBox.information(self, "저장 완료", f"설정이 저장되었습니다.\n이름: {name}")
