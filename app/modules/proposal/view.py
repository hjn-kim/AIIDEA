from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QDateEdit,
    QTabWidget, QScrollArea, QFrame, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, QDate

from app.modules.proposal.model import Proposal
from app.modules.proposal.templates import PROPOSAL_TEMPLATES
from app.ai_client import AIWorker


class ProposalWidget(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._section_editors: dict[str, QTextEdit] = {}
        self._target_section = ""
        self._auto_fill_sections: list[str] = []
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
        layout.setSpacing(20)

        # ── 헤더 ──────────────────────────────────────
        header = QHBoxLayout()
        title_lbl = QLabel("제안서")
        title_lbl.setObjectName("pageTitle")
        header.addWidget(title_lbl)
        header.addStretch()

        self.template_combo = QComboBox()
        self.template_combo.addItems(list(PROPOSAL_TEMPLATES.keys()))
        self.template_combo.currentTextChanged.connect(self._on_template_changed)
        header.addWidget(QLabel("템플릿:"))
        header.addWidget(self.template_combo)

        clear_btn = QPushButton("초기화")
        clear_btn.setObjectName("secondaryButton")
        clear_btn.clicked.connect(self._clear)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        # ── 기본 정보 ──────────────────────────────────
        layout.addWidget(self._sep("기본 정보"))

        row1 = QHBoxLayout()
        self.title_input = self._field("제안서 제목을 입력하세요")
        row1.addWidget(self._labeled("제안 제목", self.title_input), 3)
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy년 MM월 dd일")
        row1.addWidget(self._labeled("제안 일자", self.date_input), 2)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.from_input = self._field("제안사 이름")
        row2.addWidget(self._labeled("제안사 (From)", self.from_input))
        self.to_input = self._field("수신 기업명")
        row2.addWidget(self._labeled("수신사 (To)", self.to_input))
        layout.addLayout(row2)

        # ── 섹션 탭 ──────────────────────────────────
        layout.addWidget(self._sep("제안서 섹션"))

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self._build_section_tabs(list(PROPOSAL_TEMPLATES.values())[0])

        # ── AI 어시스턴트 ────────────────────────────
        layout.addWidget(self._sep("AI 어시스턴트"))

        ai_row = QHBoxLayout()
        self.btn_section_ai = QPushButton("현재 섹션 AI 작성")
        self.btn_section_ai.setObjectName("aiButton")
        self.btn_section_ai.clicked.connect(self._ai_section)
        ai_row.addWidget(self.btn_section_ai)
        self.btn_save = QPushButton("AI 최종제안서 작성")
        self.btn_save.setObjectName("aiButton")
        self.btn_save.clicked.connect(self._save_proposal)
        ai_row.addWidget(self.btn_save)
        ai_row.addStretch()
        layout.addLayout(ai_row)

        layout.addStretch()

    def _build_section_tabs(self, sections: list[str]):
        self.tabs.clear()
        self._section_editors.clear()
        for section in sections:
            editor = QTextEdit()
            editor.setPlaceholderText(f"{section} 내용을 입력하거나 AI로 생성하세요...")
            editor.setMinimumHeight(200)
            self._section_editors[section] = editor
            self.tabs.addTab(editor, section)

    def _on_template_changed(self, template_name: str):
        sections = PROPOSAL_TEMPLATES.get(template_name, [])
        self._build_section_tabs(sections)

    # ── AI ──────────────────────────────────────────
    def _ai_section(self):
        current_idx = self.tabs.currentIndex()
        if current_idx < 0:
            return
        section_name = self.tabs.tabText(current_idx)
        context_parts = []
        for name, editor in self._section_editors.items():
            txt = editor.toPlainText().strip()
            if txt and name != section_name:
                context_parts.append(f"[{name}]\n{txt}")

        from app.modules.db.storage import DocumentDB
        db_context = DocumentDB.get_context_text()

        prompt = (
            f"제안서 제목: {self.title_input.text()}\n"
            f"템플릿 유형: {self.template_combo.currentText()}\n"
            f"제안사: {self.from_input.text()}\n"
            f"수신사: {self.to_input.text()}\n\n"
            + (f"[참고 자료]\n{db_context}\n\n" if db_context else "")
            + f"기존 작성된 섹션들:\n" + "\n\n".join(context_parts) + "\n\n"
            f"지금 작성해야 할 섹션: '{section_name}'\n\n"
            f"위 맥락을 참고하여 '{section_name}' 섹션의 내용을 전문적으로 작성하세요."
        )
        self._run_ai(prompt, "proposal_section", target_section=section_name)

    def _run_ai(self, prompt: str, system_key: str, target_section: str = ""):
        self.btn_section_ai.setEnabled(False)
        self.status_message.emit("AI 작성 중...")
        self._target_section = target_section

        self._worker = AIWorker(prompt, system_key)
        self._worker.result_ready.connect(self._on_ai_result)
        self._worker.error_occurred.connect(self._on_ai_error)
        self._worker.finished.connect(lambda: self.btn_section_ai.setEnabled(True))
        self._worker.start()

    def _on_ai_result(self, text: str):
        if self._target_section and self._target_section in self._section_editors:
            self._section_editors[self._target_section].setPlainText(text)
            self.status_message.emit(f"'{self._target_section}' 섹션 AI 작성 완료")
        self._target_section = ""

    def _on_ai_error(self, error: str):
        QMessageBox.critical(self, "AI 오류", f"Gemini API 오류:\n{error}")
        self.status_message.emit("AI 오류 발생")

    # ── 저장 ──────────────────────────────────────────
    def _get_model(self) -> Proposal:
        return Proposal(
            title=self.title_input.text().strip(),
            date=self.date_input.text(),
            from_company=self.from_input.text().strip(),
            to_company=self.to_input.text().strip(),
            template_name=self.template_combo.currentText(),
            sections={k: v.toPlainText() for k, v in self._section_editors.items()},
        )

    def _save_proposal(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "입력 확인", "제안 제목을 입력하세요.")
            return

        from app.logger import log_usage
        log_usage("제안서", self.title_input.text().strip())

        empty_sections = [
            name for name, editor in self._section_editors.items()
            if not editor.toPlainText().strip()
        ]

        if empty_sections:
            msg = QMessageBox(self)
            msg.setWindowTitle("빈 섹션 처리")
            msg.setText(
                f"다음 섹션이 비어있습니다:\n  • " +
                "\n  • ".join(empty_sections) +
                "\n\n어떻게 처리하시겠습니까?"
            )
            btn_blank = msg.addButton("빈칸으로 저장", QMessageBox.ButtonRole.AcceptRole)
            btn_ai = msg.addButton("AI로 자동 채우기", QMessageBox.ButtonRole.ActionRole)
            msg.addButton("취소", QMessageBox.ButtonRole.RejectRole)
            msg.exec()

            clicked = msg.clickedButton()
            if clicked == btn_ai:
                self._auto_fill_and_save(empty_sections)
                return
            elif clicked != btn_blank:
                return

        self._do_save()

    def _auto_fill_and_save(self, sections: list[str]):
        self._auto_fill_sections = list(sections)
        self.btn_save.setEnabled(False)
        self.btn_section_ai.setEnabled(False)
        self._fill_next_auto()

    def _fill_next_auto(self):
        if not self._auto_fill_sections:
            self.btn_save.setEnabled(True)
            self.btn_section_ai.setEnabled(True)
            self._do_save()
            return

        section_name = self._auto_fill_sections[0]
        context_parts = []
        for name, editor in self._section_editors.items():
            txt = editor.toPlainText().strip()
            if txt and name != section_name:
                context_parts.append(f"[{name}]\n{txt}")

        from app.modules.db.storage import DocumentDB
        db_context = DocumentDB.get_context_text()

        prompt = (
            f"제안서 제목: {self.title_input.text()}\n"
            f"템플릿 유형: {self.template_combo.currentText()}\n"
            f"제안사: {self.from_input.text()}\n"
            f"수신사: {self.to_input.text()}\n\n"
            + (f"[참고 자료]\n{db_context}\n\n" if db_context else "")
            + f"기존 작성된 섹션들:\n" + "\n\n".join(context_parts) + "\n\n"
            f"지금 작성해야 할 섹션: '{section_name}'\n\n"
            f"위 맥락을 참고하여 '{section_name}' 섹션의 내용을 전문적으로 작성하세요."
        )

        remaining = len(self._auto_fill_sections)
        self.status_message.emit(f"'{section_name}' AI 작성 중... (남은 {remaining}개)")
        self._target_section = section_name

        self._worker = AIWorker(prompt, "proposal_section")
        self._worker.result_ready.connect(self._on_auto_fill_result)
        self._worker.error_occurred.connect(self._on_auto_fill_error)
        self._worker.start()

    def _on_auto_fill_result(self, text: str):
        if self._target_section and self._target_section in self._section_editors:
            self._section_editors[self._target_section].setPlainText(text)
        if self._auto_fill_sections:
            self._auto_fill_sections.pop(0)
        self._fill_next_auto()

    def _on_auto_fill_error(self, error: str):
        self.btn_save.setEnabled(True)
        self.btn_section_ai.setEnabled(True)
        self._auto_fill_sections.clear()
        QMessageBox.critical(self, "AI 오류", f"자동 채우기 중 오류:\n{error}")
        self.status_message.emit("AI 자동 채우기 오류 발생")

    def _do_save(self):
        from app.modules.proposal.exporter import export_docx
        try:
            path = export_docx(self._get_model())
            QMessageBox.information(self, "저장 완료", f"파일이 저장되었습니다:\n{path}")
            self.status_message.emit(f"저장: {path}")
        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))

    def _clear(self):
        reply = QMessageBox.question(self, "초기화", "모든 내용을 초기화하시겠습니까?")
        if reply == QMessageBox.StandardButton.Yes:
            self.title_input.clear()
            self.date_input.setDate(QDate.currentDate())
            self.from_input.clear()
            self.to_input.clear()
            for editor in self._section_editors.values():
                editor.clear()

    # ── 헬퍼 ──────────────────────────────────────────
    def _field(self, placeholder: str) -> QLineEdit:
        w = QLineEdit()
        w.setPlaceholderText(placeholder)
        return w

    def _labeled(self, label_text: str, widget: QWidget) -> QWidget:
        container = QWidget()
        vl = QVBoxLayout(container)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(4)
        lbl = QLabel(label_text)
        lbl.setObjectName("sectionLabel")
        vl.addWidget(lbl)
        vl.addWidget(widget)
        return container

    def _sep(self, text: str) -> QWidget:
        container = QWidget()
        hl = QHBoxLayout(container)
        hl.setContentsMargins(0, 4, 0, 0)
        lbl = QLabel(text)
        lbl.setObjectName("sectionLabel")
        hl.addWidget(lbl)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hl.addWidget(line)
        return container
