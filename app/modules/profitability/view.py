from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QSizePolicy,
    QDoubleSpinBox, QSpinBox, QStyledItemDelegate,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import re


class _ComboDelegate(QStyledItemDelegate):
    """열별 드롭다운 선택을 지원하는 델리게이트 — 셀은 일반 텍스트로 표시됨."""

    def __init__(self, items: list, parent=None):
        super().__init__(parent)
        self._items = items

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(self._items)
        return combo

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.DisplayRole) or ""
        idx = self._items.index(value) if value in self._items else 0
        editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

from app.modules.profitability.model import (
    ProfitabilityData, ProfitabilityCalculator, CostItem, RevenueItem
)
from app.ai_client import AIWorker


class ProfitabilityWidget(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._input_setup_worker = None
        self._chart_cashflow = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── 헤더 ──────────────────────────────────────
        header = QHBoxLayout()
        title_lbl = QLabel("수익성 분석 모델")
        title_lbl.setObjectName("pageTitle")
        header.addWidget(title_lbl)
        header.addStretch()
        export_btn = QPushButton("Excel 내보내기")
        export_btn.clicked.connect(self._export_xlsx)
        header.addWidget(export_btn)
        layout.addLayout(header)

        # ── 탭 ──────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.tabs, 1)

        self.tabs.addTab(self._build_setup_tab(),         "기본 설정")
        self.tabs.addTab(self._build_input_suggest_tab(), "AI 인풋값 제안")
        self.tabs.addTab(self._build_results_tab(),       "결과")

    # ── 탭 0: 기본 설정 ───────────────────────────
    def _build_setup_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        def _labeled_w(label: str, widget, hint: str = "") -> QWidget:
            c = QWidget()
            vl = QVBoxLayout(c)
            vl.setContentsMargins(0, 0, 0, 0)
            vl.setSpacing(4)
            lbl = QLabel(label)
            lbl.setObjectName("sectionLabel")
            vl.addWidget(lbl)
            vl.addWidget(widget)
            if hint:
                h = QLabel(hint)
                h.setStyleSheet("color: #6E6E80; font-size: 9px;")
                h.setWordWrap(True)
                vl.addWidget(h)
            return c

        # 프로젝트명
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("프로젝트 이름")
        r0 = QHBoxLayout()
        r0.addWidget(_labeled_w("프로젝트명", self.project_name), 3)
        r0.addStretch(1)
        layout.addLayout(r0)

        # 사업 아이템 | 지역
        self.business_item_input = QLineEdit()
        self.business_item_input.setPlaceholderText("사업 아이템")
        self.region_input = QLineEdit()
        self.region_input.setPlaceholderText("지역")
        r1 = QHBoxLayout()
        r1.addWidget(_labeled_w("사업 아이템", self.business_item_input), 2)
        r1.addWidget(_labeled_w("지역", self.region_input), 2)
        r1.addStretch(3)
        layout.addLayout(r1)

        # 사업 설명
        self.business_desc_input = QLineEdit()
        self.business_desc_input.setPlaceholderText("사업 내용 설명")
        r2 = QHBoxLayout()
        r2.addWidget(_labeled_w("사업 설명", self.business_desc_input), 3)
        r2.addStretch(1)
        layout.addLayout(r2)

        # 0년차 연도 | 분석기간 | 통화
        self.base_year_spin = QSpinBox()
        self.base_year_spin.setRange(2000, 2100)
        self.base_year_spin.setValue(2026)
        self.period_spin = QSpinBox()
        self.period_spin.setRange(1, 40)
        self.period_spin.setValue(3)
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "KRW", "EUR", "JPY"])
        self.exchange_rate_spin = QDoubleSpinBox()
        self.exchange_rate_spin.setRange(0.001, 100000.0)
        self.exchange_rate_spin.setDecimals(2)
        self.exchange_rate_spin.setValue(1300.0)
        self.exchange_rate_spin.setSuffix(" 원/1외화")
        self.currency_combo.currentTextChanged.connect(self._on_currency_changed)
        r3 = QHBoxLayout()
        r3.addWidget(_labeled_w("0년차 연도", self.base_year_spin), 2)
        r3.addWidget(_labeled_w("분석 기간 (년)", self.period_spin), 2)
        r3.addWidget(_labeled_w("통화", self.currency_combo), 1)
        r3.addWidget(_labeled_w("환율 (원 환산 기준)", self.exchange_rate_spin), 2)
        r3.addStretch(1)
        layout.addLayout(r3)

        # 할인율 | 비용 연간 증가율
        self.discount_rate_spin = QDoubleSpinBox()
        self.discount_rate_spin.setRange(0, 100)
        self.discount_rate_spin.setDecimals(1)
        self.discount_rate_spin.setValue(10.0)
        self.discount_rate_spin.setSuffix(" %")
        self.cost_growth_spin = QDoubleSpinBox()
        self.cost_growth_spin.setRange(-100, 500)
        self.cost_growth_spin.setDecimals(1)
        self.cost_growth_spin.setValue(0.0)
        self.cost_growth_spin.setSuffix(" %")
        r4 = QHBoxLayout()
        r4.addWidget(_labeled_w("할인율", self.discount_rate_spin,
                                "NPV 계산에 사용되는 연간 할인율"), 2)
        r4.addWidget(_labeled_w("비용 연간 증가율", self.cost_growth_spin,
                                "운영 비용이 매년 이 비율로 증가"), 2)
        r4.addStretch(3)
        layout.addLayout(r4)
        layout.addSpacing(70)

        # 통화 초기 상태 적용
        self._on_currency_changed(self.currency_combo.currentText())

        # AI 인풋값 제안 버튼
        ai_btn_row = QHBoxLayout()
        self.btn_ai_input_setup = QPushButton("AI 인풋값 제안")
        self.btn_ai_input_setup.setObjectName("aiButton")
        self.btn_ai_input_setup.clicked.connect(self._ai_input_setup)
        ai_btn_row.addWidget(self.btn_ai_input_setup)
        ai_btn_row.addStretch()
        layout.addLayout(ai_btn_row)
        layout.addStretch()

        return w

    # ── 탭 1: AI 인풋값 제안 ──────────────────────
    def _build_input_suggest_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        hint = QLabel(
            "수익성 분석에 필요한 모든 비용·수익 항목을 입력하세요.  "
            "연별 항목은 연간 금액, 일회성 항목은 총액을 입력합니다."
        )
        hint.setStyleSheet("color: #6E6E80; font-size: 9px; padding: 0 0 4px 0;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        hdr = QHBoxLayout()
        add_btn = QPushButton("+ 행 추가")
        add_btn.clicked.connect(self._add_input_suggestion_row)
        hdr.addWidget(add_btn)
        del_btn = QPushButton("- 행 삭제")
        del_btn.setObjectName("dangerButton")
        del_btn.clicked.connect(self._del_input_suggestion_row)
        hdr.addWidget(del_btn)
        hdr.addStretch()
        layout.addLayout(hdr)

        # 열: 구분(0)|항목명(1)|유형(2)|주기(3)|설명(4)|계산식(5)|예상금액(6)|원환산(7)
        self.input_suggestion_table = QTableWidget(0, 8)
        self.input_suggestion_table.setHorizontalHeaderLabels(
            ["구분", "항목명", "유형", "주기", "설명", "계산식", "예상 금액", "원 환산"]
        )
        hh = self.input_suggestion_table.horizontalHeader()
        for col in range(8):
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
        self.input_suggestion_table.setColumnWidth(0, 80)   # 구분
        self.input_suggestion_table.setColumnWidth(1, 150)  # 항목명
        self.input_suggestion_table.setColumnWidth(2, 100)  # 유형
        self.input_suggestion_table.setColumnWidth(3, 90)   # 주기
        self.input_suggestion_table.setColumnWidth(4, 240)  # 설명
        self.input_suggestion_table.setColumnWidth(5, 200)  # 계산식
        self.input_suggestion_table.setColumnWidth(6, 150)  # 예상금액
        self.input_suggestion_table.setColumnWidth(7, 140)  # 원환산
        self.input_suggestion_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.input_suggestion_table.verticalHeader().setDefaultSectionSize(32)

        # 드롭다운 델리게이트 (클릭 시에만 combo 표시, 평소엔 일반 텍스트)
        self._del_구분 = _ComboDelegate(["비용", "수익"], self.input_suggestion_table)
        self._del_유형 = _ComboDelegate(["고정비", "변동비", "-"], self.input_suggestion_table)
        self._del_주기 = _ComboDelegate(["연별", "일회성"], self.input_suggestion_table)
        self.input_suggestion_table.setItemDelegateForColumn(0, self._del_구분)
        self.input_suggestion_table.setItemDelegateForColumn(2, self._del_유형)
        self.input_suggestion_table.setItemDelegateForColumn(3, self._del_주기)

        layout.addWidget(self.input_suggestion_table)

        calc_row = QHBoxLayout()
        self.btn_calc_results = QPushButton("결과 계산  →")
        self.btn_calc_results.setObjectName("aiButton")
        self.btn_calc_results.setMinimumHeight(38)
        self.btn_calc_results.clicked.connect(self._go_to_results)
        calc_row.addWidget(self.btn_calc_results)
        calc_row.addStretch()
        layout.addLayout(calc_row)

        return w

    # ── 탭 2: 결과 ────────────────────────────────
    def _build_results_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # KPI 카드 행
        self.kpi_layout = QHBoxLayout()
        layout.addLayout(self.kpi_layout)
        self._kpi_widgets = {}
        for label in ["총 수익", "총 비용", "순이익", "ROI", "손익분기점"]:
            card, val_lbl = self._kpi_card(label, "-")
            self.kpi_layout.addWidget(card)
            self._kpi_widgets[label] = val_lbl

        # 연도별 수익성 테이블
        yr_lbl = QLabel("연도별 수익성 추정")
        yr_lbl.setObjectName("sectionLabel")
        layout.addWidget(yr_lbl)

        self.yearly_table = QTableWidget(0, 6)
        self.yearly_table.setObjectName("yearlyResultTable")
        self.yearly_table.setHorizontalHeaderLabels(
            ["연도", "수익", "비용", "순이익", "누적현금흐름", "ROI"]
        )
        self.yearly_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.yearly_table.verticalHeader().setDefaultSectionSize(40)
        self.yearly_table.setMinimumHeight(120)
        self.yearly_table.setMaximumHeight(520)
        self.yearly_table.setStyleSheet("""
            QTableWidget#yearlyResultTable {
                background-color: #171717;
                gridline-color: #3A3A3A;
            }
            QTableWidget#yearlyResultTable::item {
                color: #ECECEC;
                font-size: 10pt;
                padding: 6px 12px;
            }
            QTableWidget#yearlyResultTable::item:selected {
                background-color: #0D3B5E;
                color: #ECECEC;
            }
            QTableWidget#yearlyResultTable QHeaderView::section {
                background-color: #212121;
                color: #8E8EA0;
                font-size: 10pt;
                font-weight: bold;
                padding: 8px 12px;
            }
        """)
        yh = self.yearly_table.horizontalHeader()
        yh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for col in range(1, 6):
            yh.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.yearly_table)

        # 차트 영역
        self.charts_container = QVBoxLayout()
        layout.addLayout(self.charts_container)

        self.chart_placeholder = QLabel("'결과 계산' 버튼을 눌러 차트를 생성하세요.")
        self.chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_placeholder.setStyleSheet("color: #6E6E80; padding: 40px;")
        self.charts_container.addWidget(self.chart_placeholder)

        # AI 분석 리포트
        ai_row = QHBoxLayout()
        self.btn_ai_analysis = QPushButton("AI 재무 분석 리포트 생성")
        self.btn_ai_analysis.setObjectName("aiButton")
        self.btn_ai_analysis.clicked.connect(self._ai_analysis)
        ai_row.addWidget(self.btn_ai_analysis)
        ai_row.addStretch()
        layout.addLayout(ai_row)

        self.ai_output = QTextEdit()
        self.ai_output.setPlaceholderText("AI 재무 분석 리포트가 여기에 표시됩니다...")
        self.ai_output.setMinimumHeight(180)
        layout.addWidget(self.ai_output)

        return w

    def _kpi_card(self, label: str, value: str) -> tuple:
        card = QFrame()
        card.setObjectName("kpiCard")
        card.setStyleSheet("""
            QFrame#kpiCard {
                background-color: #212121;
                border: 1px solid #3A3A3A;
                border-radius: 10px;
                padding: 16px;
            }
            QFrame#kpiCard QLabel#kpiCardLabel {
                color: #8E8EA0;
                font-size: 10pt;
                font-weight: bold;
            }
            QFrame#kpiCard QLabel#kpiCardValue {
                color: #ECECEC;
                font-size: 14pt;
                font-weight: bold;
            }
        """)
        card_layout = QVBoxLayout(card)
        lbl = QLabel(label)
        lbl.setObjectName("kpiCardLabel")
        val_lbl = QLabel(value)
        val_lbl.setObjectName("kpiCardValue")
        card_layout.addWidget(lbl)
        card_layout.addWidget(val_lbl)
        return card, val_lbl

    # ── 데이터 수집 ──────────────────────────────
    def _collect_data(self) -> ProfitabilityData:
        period_year = self.period_spin.value()
        data = ProfitabilityData(
            project_name=self.project_name.text().strip(),
            region=self.region_input.text().strip(),
            business_item=self.business_item_input.text().strip(),
            business_description=self.business_desc_input.text().strip(),
            base_year=self.base_year_spin.value(),
            period_year=period_year,
            currency=self.currency_combo.currentText(),
            exchange_rate_to_krw=self.exchange_rate_spin.value(),
            discount_rate=self.discount_rate_spin.value(),
            cost_growth_rate=self.cost_growth_spin.value(),
        )

        for row in range(self.input_suggestion_table.rowCount()):
            try:
                구분 = (self.input_suggestion_table.item(row, 0) or QTableWidgetItem("비용")).text() or "비용"
                항목명 = (self.input_suggestion_table.item(row, 1) or QTableWidgetItem("")).text()
                유형 = (self.input_suggestion_table.item(row, 2) or QTableWidgetItem("고정비")).text() or "고정비"
                주기 = (self.input_suggestion_table.item(row, 3) or QTableWidgetItem("연별")).text() or "연별"
                금액_txt = (self.input_suggestion_table.item(row, 6) or QTableWidgetItem("0")).text()
                금액 = float(re.sub(r"[^\d.]", "", 금액_txt) or 0)

                if 구분 == "비용":
                    data.cost_items.append(
                        CostItem(name=항목명, category=유형, amount=금액, period=주기)
                    )
                else:  # 수익
                    qty = period_year if 주기 == "연별" else 1
                    data.revenue_items.append(
                        RevenueItem(name=항목명, unit_price=금액, quantity=qty)
                    )
            except (ValueError, AttributeError):
                pass

        return data

    # ── 결과 계산 & 탭 이동 ──────────────────────
    def _go_to_results(self):
        if self.input_suggestion_table.rowCount() == 0:
            QMessageBox.warning(self, "데이터 없음", "AI 인풋값 제안 탭에 항목을 먼저 입력하세요.")
            return
        self._refresh_results()
        self.tabs.setCurrentIndex(2)

    # ── 계산 갱신 ────────────────────────────────
    def _refresh_results(self):
        data = self._collect_data()
        calc = ProfitabilityCalculator(data)

        bep = calc.breakeven_years()
        bep_str = f"{bep:.1f}년" if bep != float("inf") else "도달 불가"
        profit = calc.net_profit()

        self._kpi_widgets["총 수익"].setText(calc.format_currency(calc.total_revenue()))
        self._kpi_widgets["총 비용"].setText(calc.format_currency(calc.total_cost()))
        self._kpi_widgets["순이익"].setText(calc.format_currency(profit))
        self._kpi_widgets["순이익"].setStyleSheet(
            "color: #4ADE80; font-size: 14pt; font-weight: bold;" if profit >= 0
            else "color: #EF4444; font-size: 14pt; font-weight: bold;"
        )
        self._kpi_widgets["ROI"].setText(f"{calc.profit_margin():.1f}%")
        self._kpi_widgets["손익분기점"].setText(bep_str)

        # 연도별 테이블 갱신
        self.yearly_table.setRowCount(0)
        for yr_data in calc.yearly_cashflow():
            r = self.yearly_table.rowCount()
            self.yearly_table.insertRow(r)
            self.yearly_table.setRowHeight(r, 40)
            self.yearly_table.setItem(r, 0, QTableWidgetItem(yr_data["연도"]))
            for col, key in enumerate(["수익", "비용", "순이익", "누적현금흐름"], start=1):
                item = QTableWidgetItem(calc.format_currency(yr_data[key]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if key == "순이익":
                    item.setForeground(
                        QColor("#EF4444") if yr_data[key] < 0 else QColor("#4ADE80")
                    )
                elif key == "누적현금흐름":
                    item.setForeground(
                        QColor("#EF4444") if yr_data[key] < 0 else QColor("#38BDF8")
                    )
                self.yearly_table.setItem(r, col, item)
            roi_item = QTableWidgetItem(
                f"{yr_data['ROI']:.1f}%" if yr_data["ROI"] != 0.0 else "-"
            )
            roi_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.yearly_table.setItem(r, 5, roi_item)

        self._rebuild_chart(calc)
        self.status_message.emit("계산 완료")

    def _rebuild_chart(self, calc):
        if self._chart_cashflow:
            self._chart_cashflow.setParent(None)
            self._chart_cashflow = None
        if self.chart_placeholder.parent():
            self.chart_placeholder.setParent(None)

        from app.modules.profitability.charts import make_cashflow_chart
        flows = calc.yearly_cashflow_simple()
        self._chart_cashflow = make_cashflow_chart(flows, "누적 현금흐름")
        self.charts_container.addWidget(self._chart_cashflow)

    # ── AI 재무 분석 ────────────────────────────
    def _ai_analysis(self):
        data = self._collect_data()
        if not data.cost_items and not data.revenue_items:
            QMessageBox.warning(self, "데이터 없음", "인풋값 제안 탭에 항목을 먼저 입력하세요.")
            return
        calc = ProfitabilityCalculator(data)
        bep = calc.breakeven_years()

        yr_lines = "\n".join(
            f"  {yr['연도']}: 수익 {calc.format_currency(yr['수익'])} / "
            f"비용 {calc.format_currency(yr['비용'])} / "
            f"순이익 {calc.format_currency(yr['순이익'])} / "
            f"누적현금 {calc.format_currency(yr['누적현금흐름'])}"
            for yr in calc.yearly_cashflow()
        )
        cost_lines = "\n".join(
            f"  - {c.name}: {calc.format_currency(c.amount)} ({c.category}, {c.period})"
            for c in data.cost_items if c.name
        )
        rev_lines = "\n".join(
            f"  - {r.name}: 연간 {calc.format_currency(r.unit_price)} × {int(r.quantity)}년 = {calc.format_currency(r.total)}"
            for r in data.revenue_items if r.name
        )

        prompt = (
            f"당신은 전문 재무 분가입니다. 아래 수익성 분석 데이터를 바탕으로 심층 재무 분석 리포트를 한국어로 작성하세요.\n\n"
            f"[기본 정보]\n"
            f"프로젝트: {data.project_name} | 지역: {data.region} | 사업: {data.business_item}\n"
            f"분석 기간: {data.period_year}년 (0년차: {data.base_year}년) | 통화: {data.currency}\n"
            f"할인율: {data.discount_rate}% | 비용 증가율: {data.cost_growth_rate}%\n\n"
            f"[재무 요약]\n"
            f"총 수익: {calc.format_currency(calc.total_revenue())}\n"
            f"총 비용: {calc.format_currency(calc.total_cost())}  (고정비 {calc.format_currency(calc.total_fixed_cost())} / 변동비 {calc.format_currency(calc.total_variable_cost())})\n"
            f"순이익: {calc.format_currency(calc.net_profit())} | ROI: {calc.profit_margin():.1f}%\n"
            f"손익분기점: {bep:.1f}년\n\n"
            f"[연도별 추정]\n{yr_lines}\n\n"
            f"[비용 내역]\n{cost_lines}\n\n"
            f"[수익 내역]\n{rev_lines}\n\n"
            f"[요청사항]\n"
            f"1. 수익성 종합 평가 (투자 매력도, ROI 수준, 손익분기 도달 가능성)\n"
            f"2. 핵심 리스크 요인 및 대응 방안\n"
            f"3. 수익 개선을 위한 구체적 전략 제언\n"
            f"4. 결론 및 투자 권고"
        )

        self.btn_ai_analysis.setEnabled(False)
        self.status_message.emit("AI 재무 분석 중...")
        self._worker = AIWorker(prompt, "profitability_analysis", model="gemini-2.5-pro")
        self._worker.result_ready.connect(self._on_ai_result)
        self._worker.error_occurred.connect(self._on_ai_error)
        self._worker.finished.connect(lambda: self.btn_ai_analysis.setEnabled(True))
        self._worker.start()

    def _on_ai_result(self, text: str):
        self.ai_output.setPlainText(text)
        self.status_message.emit("AI 분석 완료")

    def _on_ai_error(self, error: str):
        QMessageBox.critical(self, "AI 오류", f"Gemini API 오류:\n{error}")
        self.status_message.emit("AI 오류 발생")

    # ── AI 인풋값 제안 ────────────────────────────
    def _ai_input_setup(self):
        project = self.project_name.text().strip()
        if not project:
            QMessageBox.warning(self, "입력 필요", "프로젝트명을 입력하세요.")
            return

        region = self.region_input.text().strip()
        item = self.business_item_input.text().strip()
        desc = self.business_desc_input.text().strip()
        period = self.period_spin.value()

        prompt = (
            f"다음 사업의 수익성 분석에 필요한 모든 비용 및 수익 항목을 분석하세요.\n\n"
            f"사업 정보:\n"
            f"- 프로젝트명: {project}\n"
            f"- 지역: {region}\n"
            f"- 사업 아이템: {item}\n"
            f"- 사업 설명: {desc}\n"
            f"- 분석 기간: {period}년\n\n"
            f"각 항목을 아래 형식으로 한 줄씩 출력하세요.\n"
            f"마크다운·헤더·설명 텍스트 없이 데이터 행만 출력하세요:\n\n"
            f"구분|항목명|유형|주기|설명|계산식|예상금액(KRW 숫자만)\n\n"
            f"- 구분: '비용' 또는 '수익'\n"
            f"- 유형: 비용이면 '고정비' 또는 '변동비', 수익이면 '-'\n"
            f"- 주기: '연별' 또는 '일회성' (초기 장비·보증금 등은 '일회성')\n"
            f"- 비용 항목 먼저(고정비→변동비→일회성), 수익 항목 나중에 나열\n"
            f"- 해당 사업에서 실제로 발생할 수 있는 모든 항목 포함\n"
            f"- 계산식: 금액 산출 수식 (예: '단가 50,000 × 100명', 없으면 빈칸)\n"
            f"- 예상금액: 연별 항목은 연 기준 KRW 숫자, 일회성 항목은 총액 KRW 숫자"
        )

        self.btn_ai_input_setup.setEnabled(False)
        self.btn_ai_input_setup.setText("생성 중...")
        self.status_message.emit("AI 인풋값 제안 중...")

        self._input_setup_worker = AIWorker(prompt, "profitability_input_setup")
        self._input_setup_worker.result_ready.connect(self._on_input_setup_result)
        self._input_setup_worker.error_occurred.connect(self._on_input_setup_error)
        self._input_setup_worker.finished.connect(
            lambda: (self.btn_ai_input_setup.setEnabled(True),
                     self.btn_ai_input_setup.setText("AI 인풋값 제안"))
        )
        self._input_setup_worker.start()

    def _on_input_setup_result(self, text: str):
        self.input_suggestion_table.setRowCount(0)
        for line in text.strip().splitlines():
            line = line.strip()
            if not line or '|' not in line:
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 4:
                continue
            구분 = parts[0]
            if 구분 not in ("비용", "수익"):
                continue
            항목명 = parts[1]
            if len(parts) >= 7:
                유형, 주기, 설명, 계산식, 금액 = parts[2], parts[3], parts[4], parts[5], parts[6]
            elif len(parts) >= 5:
                유형 = "고정비" if 구분 == "비용" else "-"
                주기 = "연별"
                설명, 계산식, 금액 = parts[2], parts[3], parts[4]
            else:
                유형 = "고정비" if 구분 == "비용" else "-"
                주기, 설명, 계산식, 금액 = "연별", parts[2], "", parts[3]
            self._insert_suggestion_row(구분, 항목명, 유형, 주기, 설명, 계산식, 금액)
        self.tabs.setCurrentIndex(1)
        self.status_message.emit("AI 인풋값 제안 완료 — 내용 확인 후 '결과 계산' 버튼을 누르세요")

    def _on_input_setup_error(self, error: str):
        QMessageBox.critical(self, "AI 오류", f"Gemini API 오류:\n{error}")
        self.status_message.emit("AI 인풋값 제안 오류")

    def _insert_suggestion_row(self, 구분: str, 항목명: str,
                               유형: str = "고정비", 주기: str = "연별",
                               설명: str = "", 계산식: str = "", 금액: str = "0"):
        row = self.input_suggestion_table.rowCount()
        self.input_suggestion_table.insertRow(row)

        self.input_suggestion_table.setItem(row, 0, QTableWidgetItem(구분))
        self.input_suggestion_table.setItem(row, 1, QTableWidgetItem(항목명))
        self.input_suggestion_table.setItem(row, 2, QTableWidgetItem(유형 if 구분 != "수익" else "-"))
        self.input_suggestion_table.setItem(row, 3, QTableWidgetItem(주기))

        self.input_suggestion_table.setItem(row, 4, QTableWidgetItem(설명))
        self.input_suggestion_table.setItem(row, 5, QTableWidgetItem(계산식))

        # 금액 숫자 파싱
        try:
            금액_num = float(re.sub(r"[^\d.]", "", 금액) or 0)
        except (ValueError, OverflowError):
            금액_num = 0.0

        currency = self.currency_combo.currentText()
        # 연별만 단위 표시(/연), 일회성은 금액만 표시
        amt_suffix = "/연" if 주기 == "연별" else ""

        # 열 6: 예상 금액 (통화 단위 포함)
        if currency == "KRW":
            amt_display = f"₩{금액_num:,.0f}{amt_suffix}"
        elif currency == "USD":
            amt_display = f"${금액_num:,.2f}{amt_suffix}"
        elif currency == "JPY":
            amt_display = f"¥{금액_num:,.0f}{amt_suffix}"
        else:
            amt_display = f"{금액_num:,.2f} {currency}{amt_suffix}"
        amt_item = QTableWidgetItem(amt_display)
        amt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.input_suggestion_table.setItem(row, 6, amt_item)

        # 열 7: 원 환산 (KRW이면 "-")
        if currency != "KRW":
            rate = self.exchange_rate_spin.value()
            krw = 금액_num * rate
            krw_display = f"₩{krw:,.0f}{amt_suffix}"
        else:
            krw_display = "-"
        krw_item = QTableWidgetItem(krw_display)
        krw_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        krw_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.input_suggestion_table.setItem(row, 7, krw_item)

    def _on_currency_changed(self, currency: str):
        """KRW 선택 시 환율 입력 비활성화."""
        is_krw = (currency == "KRW")
        self.exchange_rate_spin.setEnabled(not is_krw)
        if is_krw:
            self.exchange_rate_spin.setValue(1.0)

    def _add_input_suggestion_row(self):
        self._insert_suggestion_row("비용", "", "고정비", "연별", "", "", "0")

    def _del_input_suggestion_row(self):
        row = self.input_suggestion_table.currentRow()
        if row >= 0:
            self.input_suggestion_table.removeRow(row)

    # ── 내보내기 ──────────────────────────────────
    def _export_xlsx(self):
        from app.modules.profitability.exporter import export_xlsx
        try:
            data = self._collect_data()
            data.ai_analysis = self.ai_output.toPlainText()
            path = export_xlsx(data)
            QMessageBox.information(self, "저장 완료", f"파일이 저장되었습니다:\n{path}")
            self.status_message.emit(f"저장: {path}")
        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))
