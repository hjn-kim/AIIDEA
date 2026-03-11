from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QDateEdit, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate

from app.modules.meeting_minutes.model import MeetingMinutes, make_meeting_prompt
from app.ai_client import AIWorker


class MeetingMinutesWidget(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── 헤더 ──────────────────────────────────────
        header = QHBoxLayout()
        title_lbl = QLabel("회의록")
        title_lbl.setObjectName("pageTitle")
        header.addWidget(title_lbl)
        header.addStretch()

        clear_btn = QPushButton("초기화")
        clear_btn.setObjectName("secondaryButton")
        clear_btn.clicked.connect(self._clear)
        header.addWidget(clear_btn)
        layout.addLayout(header)

        # ── 기본 정보 ──────────────────────────────────
        
        # 회의 일시 | 회의 장소 (2:2:3)
        row_dt_loc = QHBoxLayout()
        self.datetime_input = QDateEdit(QDate.currentDate())
        self.datetime_input.setCalendarPopup(True)
        self.datetime_input.setDisplayFormat("yyyy년 MM월 dd일")
        row_dt_loc.addWidget(self._labeled("회의 일시", self.datetime_input), 2)
        self.location_input = self._field("회의 장소 (빈칸 가능)")
        row_dt_loc.addWidget(self._labeled("회의 장소", self.location_input), 2)
        row_dt_loc.addStretch(3)
        layout.addLayout(row_dt_loc)

        # 회의 제목 (3/4 너비)
        self.title_input = self._field("회의 제목")
        row_title = QHBoxLayout()
        row_title.addWidget(self._labeled("회의 제목", self.title_input), 3)
        row_title.addStretch(1)
        layout.addLayout(row_title)

        # 회의 목적 (3/4 너비)
        self.purpose_input = self._field("회의 목적")
        row_purpose = QHBoxLayout()
        row_purpose.addWidget(self._labeled("회의 목적", self.purpose_input), 3)
        row_purpose.addStretch(1)
        layout.addLayout(row_purpose)

        # 회의 주최측 | 참석자 (1:2:1) → 합계 75% (회의 목적과 우측 끝 동일)
        row_host_att = QHBoxLayout()
        self.host_input = self._field("회의 주최 (빈칸 가능)")
        row_host_att.addWidget(self._labeled("회의 주최측", self.host_input), 1)
        self.attendees_input = self._field("참석자")
        row_host_att.addWidget(self._labeled("참석자", self.attendees_input), 2)
        row_host_att.addStretch(1)
        layout.addLayout(row_host_att)

        # ── 회의 내용 ──────────────────────────────────
        self.agenda_input = self._textedit("회의 안건 / 주요 논의 사항", 100)
        layout.addWidget(self._labeled("회의 안건 / 주요 논의 사항", self.agenda_input))

        # 세부 논의 | 결정사항 (1:1, 전체 너비 = 회의 안건과 동일)
        row_dd = QHBoxLayout()
        self.details_input = self._field("세부 논의 내용 (빈칸 가능)")
        row_dd.addWidget(self._labeled("세부 논의 내용", self.details_input), 1)
        self.decisions_input = self._field("결정사항 (빈칸 가능)")
        row_dd.addWidget(self._labeled("결정사항", self.decisions_input), 1)
        layout.addLayout(row_dd)

        # ── AI 작성 버튼 ───────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_generate = QPushButton("AI 회의록 작성")
        self.btn_generate.setObjectName("aiButton")
        self.btn_generate.setMinimumWidth(160)
        self.btn_generate.setMinimumHeight(44)
        self.btn_generate.clicked.connect(self._generate)
        btn_row.addWidget(self.btn_generate)
        layout.addLayout(btn_row)

        layout.addStretch()

    # ── 헬퍼 ─────────────────────────────────────────
    def _field(self, placeholder: str) -> QLineEdit:
        w = QLineEdit()
        w.setPlaceholderText(placeholder)
        return w

    def _textedit(self, placeholder: str, min_height: int = 100) -> QTextEdit:
        w = QTextEdit()
        w.setPlaceholderText(placeholder)
        w.setMinimumHeight(min_height)
        return w

    def _labeled(self, label_text: str, widget: QWidget) -> QWidget:
        container = QWidget()
        vl = QVBoxLayout(container)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(4)
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #FFFFFF;")
        vl.addWidget(lbl)
        vl.addWidget(widget)
        return container

    # ── AI 작성 ──────────────────────────────────────
    def _collect(self) -> MeetingMinutes:
        return MeetingMinutes(
            title=self.title_input.text().strip(),
            host=self.host_input.text().strip(),
            purpose=self.purpose_input.text().strip(),
            meeting_datetime=self.datetime_input.text().strip(),
            location=self.location_input.text().strip(),
            attendees=self.attendees_input.text().strip(),
            agenda=self.agenda_input.toPlainText().strip(),
            details=self.details_input.text().strip(),
            decisions=self.decisions_input.text().strip(),
        )

    def _generate(self):
        m = self._collect()
        if not m.title:
            QMessageBox.warning(self, "입력 필요", "회의 제목을 입력하세요.")
            return

        self._current_model = m
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("AI 작성 중...")
        self.status_message.emit("AI 회의록 작성 중...")
        from app.logger import log_usage
        log_usage("회의록", m.title)

        prompt = make_meeting_prompt(m)
        self._worker = AIWorker(prompt, "meeting_minutes")
        self._worker.result_ready.connect(self._on_result)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_result(self, text: str):
        from app.modules.meeting_minutes.exporter import export_docx
        try:
            path = export_docx(self._current_model, text)
            QMessageBox.information(self, "저장 완료", f"회의록이 저장되었습니다:\n{path}")
            self.status_message.emit(f"저장: {path}")
        except Exception as e:
            QMessageBox.critical(self, "저장 오류", str(e))

    def _on_error(self, error: str):
        QMessageBox.critical(self, "AI 오류", f"Gemini API 오류:\n{error}")
        self.status_message.emit("AI 오류 발생")

    def _on_finished(self):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("AI 회의록 작성")

    # ── 초기화 ────────────────────────────────────────
    def _clear(self):
        reply = QMessageBox.question(self, "초기화", "모든 입력 내용을 초기화하시겠습니까?")
        if reply == QMessageBox.StandardButton.Yes:
            for w in [self.title_input, self.host_input, self.purpose_input,
                      self.location_input, self.attendees_input]:
                w.clear()
            self.datetime_input.setDate(QDate.currentDate())
            for w in [self.agenda_input, self.details_input, self.decisions_input]:
                w.clear()
