import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt


class FeedbackWidget(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # 헤더
        title = QLabel("오류 & 개선사항")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        desc = QLabel("발견한 오류나 개선 아이디어를 알려주세요. 검토 후 반영하겠습니다.")
        desc.setStyleSheet("color: #9090A8; font-size: 9pt;")
        layout.addWidget(desc)

        # 제목
        lbl_subject = QLabel("제목")
        lbl_subject.setObjectName("sectionLabel")
        layout.addWidget(lbl_subject)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("오류 & 개선사항")
        layout.addWidget(self.subject_input)

        # 내용
        lbl_body = QLabel("내용")
        lbl_body.setObjectName("sectionLabel")
        layout.addWidget(lbl_body)

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("오류 상황이나 불편한 점을 작성해주시면 수정하겠습니다.")
        self.body_input.setMinimumHeight(220)
        layout.addWidget(self.body_input, 1)

        # 전송 버튼
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_send = QPushButton("전송")
        self.btn_send.setObjectName("aiButton")
        self.btn_send.clicked.connect(self._send)
        btn_row.addWidget(self.btn_send)
        layout.addLayout(btn_row)

    def _send(self):
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()

        if not subject:
            QMessageBox.warning(self, "입력 확인", "제목을 입력하세요.")
            return
        if not body:
            QMessageBox.warning(self, "입력 확인", "내용을 입력하세요.")
            return

        smtp_email = os.environ.get("SMTP_EMAIL", "")
        smtp_password = os.environ.get("SMTP_PASSWORD", "")
        receiver = os.environ.get("RECEIVER_EMAIL", "")

        if not all([smtp_email, smtp_password, receiver]):
            QMessageBox.warning(
                self, "설정 필요",
                "이메일 전송 설정이 되어있지 않습니다.\n\n"
                ".env 파일에 다음 항목을 추가하세요:\n"
                "SMTP_EMAIL=발신용Gmail주소\n"
                "SMTP_PASSWORD=Gmail앱비밀번호\n"
                "RECEIVER_EMAIL=수신이메일주소"
            )
            return

        self.btn_send.setEnabled(False)
        self.btn_send.setText("전송 중...")

        try:
            user_name = os.environ.get("USER_NAME", "").strip() or "미설정"
            msg = MIMEMultipart()
            msg["From"] = smtp_email
            msg["To"] = receiver
            msg["Subject"] = f"[AIIDEA 피드백] - {subject}"
            full_body = f"보낸 사람: {user_name}\n\n{body}"
            msg.attach(MIMEText(full_body, "plain", "utf-8"))

            with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.send_message(msg)

            QMessageBox.information(self, "전송 완료", "피드백이 전송되었습니다. 감사합니다!")
            self.subject_input.clear()
            self.body_input.clear()
            self.status_message.emit("피드백 전송 완료")

        except Exception as e:
            QMessageBox.critical(self, "전송 실패", f"이메일 전송에 실패했습니다:\n{str(e)}")
            self.status_message.emit("피드백 전송 실패")

        finally:
            self.btn_send.setEnabled(True)
            self.btn_send.setText("전송")
