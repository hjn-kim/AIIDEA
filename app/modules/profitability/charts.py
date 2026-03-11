from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt

try:
    from PyQt6.QtCharts import (
        QChart, QChartView, QLineSeries, QBarSeries, QBarSet,
        QBarCategoryAxis, QValueAxis, QPieSeries, QSplineSeries
    )
    from PyQt6.QtGui import QPainter, QColor, QFont
    HAS_CHARTS = True
except ImportError:
    HAS_CHARTS = False

import matplotlib
try:
    matplotlib.use("qtagg")
except Exception:
    try:
        matplotlib.use("Qt5Agg")
    except Exception:
        pass
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    try:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        HAS_MPL = True
    except Exception:
        HAS_MPL = False

from app.ui.styles import COLORS


def make_cashflow_chart(monthly_flows: list, title: str = "누적 현금흐름") -> QWidget:
    if HAS_CHARTS:
        return _qt_cashflow_chart(monthly_flows, title)
    elif HAS_MPL:
        return _mpl_cashflow_chart(monthly_flows, title)
    else:
        from PyQt6.QtWidgets import QLabel
        lbl = QLabel("차트를 표시하려면 PyQt6-Qt6Charts 또는 matplotlib이 필요합니다.")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl


def make_scenario_chart(scenarios: dict, title: str = "시나리오 비교") -> QWidget:
    if HAS_CHARTS:
        return _qt_scenario_chart(scenarios, title)
    elif HAS_MPL:
        return _mpl_scenario_chart(scenarios, title)
    else:
        from PyQt6.QtWidgets import QLabel
        lbl = QLabel("차트를 표시하려면 PyQt6-Qt6Charts 또는 matplotlib이 필요합니다.")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl


# ── Matplotlib 구현 (fallback) ────────────────────
def _mpl_cashflow_chart(yearly_flows: list, title: str) -> QWidget:
    fig = Figure(figsize=(6, 3.5), facecolor="#FFFFFF")
    ax = fig.add_subplot(111, facecolor="#F7F7F8")
    years = list(range(len(yearly_flows)))
    ax.plot(years, yearly_flows, color="#0D3B5E", linewidth=2.5, marker="o", markersize=5)
    ax.axhline(0, color="#ACACBE", linewidth=0.8, linestyle="--")
    ax.fill_between(years, yearly_flows, 0,
                    where=[v >= 0 for v in yearly_flows],
                    alpha=0.12, color="#0D3B5E")
    ax.fill_between(years, yearly_flows, 0,
                    where=[v < 0 for v in yearly_flows],
                    alpha=0.12, color="#DC2626")
    ax.set_title(title, color="#0D0D0D", fontsize=11, pad=10, fontweight="bold")
    ax.set_xlabel("년차", color="#6E6E80")
    ax.set_ylabel("누적 현금흐름", color="#6E6E80")
    ax.tick_params(colors="#6E6E80")
    for spine in ax.spines.values():
        spine.set_edgecolor("#E5E5E5")
    fig.tight_layout()

    canvas = FigureCanvas(fig)
    canvas.setMinimumHeight(260)
    return canvas


def _mpl_scenario_chart(scenarios: dict, title: str) -> QWidget:
    fig = Figure(figsize=(6, 3.5), facecolor="#FFFFFF")
    ax = fig.add_subplot(111, facecolor="#F7F7F8")

    names = list(scenarios.keys())
    revenues = [s["revenue"] for s in scenarios.values()]
    costs    = [s["cost"]    for s in scenarios.values()]
    profits  = [s["profit"]  for s in scenarios.values()]

    x = range(len(names))
    w = 0.25
    ax.bar([i - w for i in x], revenues, width=w, label="수익",   color="#0D3B5E", alpha=0.85)
    ax.bar([i      for i in x], costs,   width=w, label="비용",   color="#DC2626", alpha=0.85)
    ax.bar([i + w for i in x], profits,  width=w, label="순이익", color="#0D3B5E", alpha=0.85)

    ax.set_xticks(list(x))
    ax.set_xticklabels(names, color="#0D0D0D")
    ax.set_title(title, color="#0D0D0D", fontsize=11, pad=10, fontweight="bold")
    ax.tick_params(colors="#6E6E80")
    ax.legend(facecolor="#FFFFFF", edgecolor="#E5E5E5", labelcolor="#0D0D0D")
    for spine in ax.spines.values():
        spine.set_edgecolor("#E5E5E5")
    fig.tight_layout()

    canvas = FigureCanvas(fig)
    canvas.setMinimumHeight(260)
    return canvas


# ── QtCharts 구현 ─────────────────────────────────
def _qt_cashflow_chart(monthly_flows: list, title: str) -> QWidget:
    series = QSplineSeries()
    for i, v in enumerate(monthly_flows):
        series.append(i, v)
    series.setColor(QColor("#0D3B5E"))

    chart = QChart()
    chart.addSeries(series)
    chart.setTitle(title)
    chart.setBackgroundBrush(QColor("#2A2A3E"))
    chart.setTitleBrush(QColor("#E8E8F0"))
    chart.legend().hide()

    # 축을 명시적으로 생성해 Y축이 아래(작은 값)→위(큰 값)로 가도록 설정 (누적 현금흐름이 올라가야 함)
    axis_x = QValueAxis()
    axis_x.setRange(0, max(len(monthly_flows) - 1, 0))
    axis_x.setTitleText("년차")
    axis_y = QValueAxis()
    if monthly_flows:
        mn, mx = min(monthly_flows), max(monthly_flows)
        margin = (mx - mn) * 0.1 if mx != mn else abs(mn) * 0.1 or 1
        axis_y.setRange(mn - margin, mx + margin)
    axis_y.setTitleText("누적 현금흐름")
    axis_y.setReverse(False)  # False = 작은 값이 아래, 큰 값이 위 (그래프가 올라가게)
    chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
    chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
    series.attachAxis(axis_x)
    series.attachAxis(axis_y)

    view = QChartView(chart)
    view.setRenderHint(QPainter.RenderHint.Antialiasing)
    view.setMinimumHeight(240)
    return view


def _qt_scenario_chart(scenarios: dict, title: str) -> QWidget:
    revenue_set = QBarSet("수익")
    cost_set    = QBarSet("비용")
    profit_set  = QBarSet("순이익")

    revenue_set.setColor(QColor("#00BFA5"))
    cost_set.setColor(QColor("#FF5370"))
    profit_set.setColor(QColor("#0D3B5E"))

    for s in scenarios.values():
        revenue_set.append(s["revenue"])
        cost_set.append(s["cost"])
        profit_set.append(s["profit"])

    bar_series = QBarSeries()
    bar_series.append(revenue_set)
    bar_series.append(cost_set)
    bar_series.append(profit_set)

    chart = QChart()
    chart.addSeries(bar_series)
    chart.setTitle(title)
    chart.setBackgroundBrush(QColor("#2A2A3E"))
    chart.setTitleBrush(QColor("#E8E8F0"))

    categories = list(scenarios.keys())
    axis_x = QBarCategoryAxis()
    axis_x.append(categories)
    chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
    bar_series.attachAxis(axis_x)

    axis_y = QValueAxis()
    chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
    bar_series.attachAxis(axis_y)

    view = QChartView(chart)
    view.setRenderHint(QPainter.RenderHint.Antialiasing)
    view.setMinimumHeight(240)
    return view
