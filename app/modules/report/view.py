import time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QDateEdit, QComboBox,
    QFrame, QMessageBox, QSizePolicy, QScrollArea, QProgressBar,
)
from PyQt6.QtCore import pyqtSignal, QDate, QThread

from app.modules.report.model import (
    Report, STYLES,
    make_toc_prompt,
    make_section_prompt, extract_chapters, parse_response_blocks,
)
from app.ai_client import AIWorker


class ReportBuildWorker(QThread):
    progress = pyqtSignal(str)
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, report: Report, final_toc: str, parent=None):
        super().__init__(parent)
        self.report = report
        self.final_toc = final_toc

    @staticmethod
    def _generate_with_retry(client, prompt: str, max_retries: int = 4) -> str:
        wait = 5
        for attempt in range(max_retries):
            try:
                return client.generate(prompt)
            except Exception as e:
                msg = str(e).lower()
                is_rate_limit = any(k in msg for k in ("resource exhausted", "429", "quota", "rate limit"))
                if is_rate_limit and attempt < max_retries - 1:
                    time.sleep(wait)
                    wait *= 2
                else:
                    raise

    def run(self):
        try:
            from app.ai_client import GeminiClient
            from app.modules.report.exporter import save_report_docx

            client = GeminiClient.get_instance()
            chapters = extract_chapters(self.final_toc)

            if not chapters:
                self.error_occurred.emit("목차에서 챕터를 추출할 수 없습니다.\n목차 형식을 확인하세요.")
                return

            sections = {}
            summary_context = ""
            sources_all = []
            seen = set()

            for i, chapter_title in enumerate(chapters, 1):
                self.progress.emit(f"({i}/{len(chapters)}) {chapter_title} 생성 중...")
                prompt = make_section_prompt(chapter_title, self.report, summary_context)
                text = self._generate_with_retry(client, prompt)
                r, s, src = parse_response_blocks(text, chapter_title)
                sections[chapter_title] = r
                if s:
                    summary_context += f"- {chapter_title}: {s}\n"
                if src:
                    for line in src.splitlines():
                        item = line.strip()
                        if item and item not in seen:
                            seen.add(item)
                            sources_all.append(item)
                time.sleep(5)

            self.progress.emit("DOCX 저장 중...")
            path = save_report_docx(self.report, self.final_toc, sections, sources_all)
            self.result_ready.emit(path)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ReportWidget(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._build_worker = None
        self._report: Report | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(self._scroll)

        self._show_step1()

    # ── Step 1: 입력 ──────────────────────────────────────────────
    def _show_step1(self):
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # 헤더
        hdr = QHBoxLayout()
        title_lbl = QLabel("보고서")
        title_lbl.setObjectName("pageTitle")
        hdr.addWidget(title_lbl)
        hdr.addStretch()
        layout.addLayout(hdr)

        layout.addWidget(self._sep("기본 정보"))

        # 보고서 제목 (3/4 너비)
        self._title_input = self._field("보고서 제목")
        row_title = QHBoxLayout()
        row_title.addWidget(self._labeled("보고서 제목", self._title_input), 3)
        row_title.addStretch(1)
        layout.addLayout(row_title)

        # 보고서 목적 (3/4 너비)
        self._purpose_input = self._field("보고서 목적")
        row_purpose = QHBoxLayout()
        row_purpose.addWidget(self._labeled("보고서 목적", self._purpose_input), 3)
        row_purpose.addStretch(1)
        layout.addLayout(row_purpose)

        # 작성자 | 작성일
        row_meta = QHBoxLayout()
        self._author_input = self._field("작성자 이름")
        row_meta.addWidget(self._labeled("작성자", self._author_input), 2)
        self._date_input = QDateEdit(QDate.currentDate())
        self._date_input.setCalendarPopup(True)
        self._date_input.setDisplayFormat("yyyy년 MM월 dd일")
        row_meta.addWidget(self._labeled("작성일", self._date_input), 2)
        row_meta.addStretch(3)
        layout.addLayout(row_meta)

        # 서술방식 | 분량
        self._style_combo = QComboBox()
        self._style_combo.addItems(STYLES)
        self._volume_input = self._field("예: 50")
        row_style_vol = QHBoxLayout()
        row_style_vol.addWidget(self._labeled("서술방식", self._style_combo), 2)
        row_style_vol.addWidget(self._labeled("분량 (A4 페이지)", self._volume_input), 2)
        row_style_vol.addStretch(3)
        layout.addLayout(row_style_vol)

        # 요구사항
        self._req_input = QTextEdit()
        self._req_input.setPlaceholderText(
            "포함되어야 할 특별 요구사항이나 조건을 입력하세요.\n예: 국내 사례 중심, 최신 2024년 데이터 반영, 법적 검토 포함"
        )
        self._req_input.setMinimumHeight(100)
        layout.addWidget(self._labeled("요구사항 (선택)", self._req_input))

        # 목차 생성 버튼
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._toc_gen_btn = QPushButton("AI 목차 생성")
        self._toc_gen_btn.setObjectName("aiButton")
        self._toc_gen_btn.setMinimumWidth(160)
        self._toc_gen_btn.setMinimumHeight(44)
        self._toc_gen_btn.clicked.connect(self._on_gen_toc)
        btn_row.addWidget(self._toc_gen_btn)
        layout.addLayout(btn_row)

        self._restore_draft()   # 이전 입력값 복원
        layout.addStretch()
        self._scroll.setWidget(content)

    def _on_gen_toc(self):
        title = self._title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "입력 확인", "보고서 제목을 입력하세요.")
            return

        from app.modules.db.storage import DocumentDB
        requirements = self._req_input.toPlainText().strip()
        db_context = DocumentDB.get_context_text()
        if db_context:
            requirements += ("\n\n" if requirements else "") + f"[참고 자료]\n{db_context}"

        self._report = Report(
            title=title,
            purpose=self._purpose_input.text().strip(),
            author=self._author_input.text().strip(),
            date=self._date_input.text(),
            volume=self._volume_input.text().strip(),
            style=self._style_combo.currentText(),
            requirements=requirements,
        )

        self._save_draft()       # 입력값 로컬 저장
        self._toc_gen_btn.setEnabled(False)
        self._toc_gen_btn.setText("생성 중...")
        self.status_message.emit("목차 생성 중...")
        from app.logger import log_usage
        log_usage("보고서", title)

        prompt = make_toc_prompt(self._report)
        self._worker = AIWorker(prompt, "")
        self._worker.result_ready.connect(self._on_toc_ready)
        self._worker.error_occurred.connect(self._on_toc_error)
        self._worker.start()

    def _on_toc_ready(self, toc: str):
        self.status_message.emit("목차 생성 완료")
        self._show_step2(toc)

    def _on_toc_error(self, error: str):
        QMessageBox.critical(self, "목차 생성 오류", f"Gemini API 오류:\n{error}")
        self.status_message.emit("목차 생성 오류")
        self._toc_gen_btn.setEnabled(True)
        self._toc_gen_btn.setText("목차 생성")

    # ── Step 2: 목차 확인/수정 ────────────────────────────────────
    def _show_step2(self, toc: str):
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # 헤더
        hdr = QHBoxLayout()
        title_lbl = QLabel("목차 확인 및 수정")
        title_lbl.setObjectName("pageTitle")
        hdr.addWidget(title_lbl)
        hdr.addStretch()
        self._back_btn = QPushButton("처음으로")
        self._back_btn.setObjectName("secondaryButton")
        self._back_btn.clicked.connect(self._show_step1)
        hdr.addWidget(self._back_btn)
        layout.addLayout(hdr)

        # 생성된 목차 (직접 편집 가능)
        layout.addWidget(self._sep("생성된 목차"))
        self._toc_edit = QTextEdit()
        self._toc_edit.setPlainText(toc)
        self._toc_edit.setMinimumHeight(200)
        layout.addWidget(self._toc_edit, stretch=1)

        # 진행 상황
        self._progress_label = QLabel("")
        self._progress_label.setObjectName("sectionLabel")
        self._progress_label.setVisible(False)
        layout.addWidget(self._progress_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 0)  # indeterminate
        self._progress_bar.setFixedHeight(4)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        # 버튼 행
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._build_btn = QPushButton("보고서 생성")
        self._build_btn.setObjectName("aiButton")
        self._build_btn.setMinimumWidth(180)
        self._build_btn.setMinimumHeight(44)
        self._build_btn.clicked.connect(self._on_build_report)
        btn_row.addWidget(self._build_btn)
        layout.addLayout(btn_row)
        self._scroll.setWidget(content)

    def _on_build_report(self):
        final_toc = self._toc_edit.toPlainText().strip()
        if not final_toc:
            QMessageBox.warning(self, "입력 확인", "목차가 비어 있습니다.")
            return

        self._build_btn.setEnabled(False)
        self._back_btn.setEnabled(False)
        self._progress_label.setVisible(True)
        self._progress_label.setText("보고서 생성을 시작합니다...")
        self._progress_bar.setVisible(True)
        self.status_message.emit("보고서 생성 중...")

        self._build_worker = ReportBuildWorker(self._report, final_toc)
        self._build_worker.progress.connect(self._on_build_progress)
        self._build_worker.result_ready.connect(self._on_build_done)
        self._build_worker.error_occurred.connect(self._on_build_error)
        self._build_worker.start()

    def _on_build_progress(self, msg: str):
        self._progress_label.setText(msg)
        self.status_message.emit(msg)

    def _on_build_done(self, path: str):
        self._build_btn.setEnabled(True)
        self._back_btn.setEnabled(True)
        self._progress_label.setVisible(False)
        self._progress_bar.setVisible(False)
        self.status_message.emit(f"저장: {path}")
        QMessageBox.information(self, "저장 완료", f"보고서가 저장되었습니다:\n{path}")
        self._show_step1()

    def _on_build_error(self, error: str):
        self._build_btn.setEnabled(True)
        self._back_btn.setEnabled(True)
        self._progress_label.setVisible(False)
        self._progress_bar.setVisible(False)
        QMessageBox.critical(self, "보고서 생성 오류", f"오류:\n{error}")
        self.status_message.emit("보고서 생성 오류")

    # ── 입력값 로컬 저장/복원 ──────────────────────────────────────
    @staticmethod
    def _draft_settings():
        from PyQt6.QtCore import QSettings
        return QSettings("AIIDEA", "report_draft")

    def _save_draft(self):
        s = self._draft_settings()
        s.setValue("title",        self._title_input.text())
        s.setValue("purpose",      self._purpose_input.text())
        s.setValue("author",       self._author_input.text())
        s.setValue("volume",       self._volume_input.text())
        s.setValue("style",        self._style_combo.currentIndex())
        s.setValue("requirements", self._req_input.toPlainText())

    def _restore_draft(self):
        s = self._draft_settings()
        self._title_input.setText(s.value("title",   ""))
        self._purpose_input.setText(s.value("purpose", ""))
        self._author_input.setText(s.value("author",  ""))
        self._volume_input.setText(s.value("volume",  ""))
        try:
            idx = int(s.value("style", 0))
        except (TypeError, ValueError):
            idx = 0
        if 0 <= idx < self._style_combo.count():
            self._style_combo.setCurrentIndex(idx)
        self._req_input.setPlainText(s.value("requirements", ""))

    # ── 헬퍼 ──────────────────────────────────────────────────────
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
