import dataclasses
from typing import List, Dict


@dataclasses.dataclass
class CostItem:
    name: str = ""
    category: str = "고정비"   # "고정비" | "변동비"
    amount: float = 0.0
    period: str = "연별"       # "연별" | "일회성"
    note: str = ""


@dataclasses.dataclass
class RevenueItem:
    name: str = ""
    unit_price: float = 0.0
    quantity: float = 0.0
    note: str = ""

    @property
    def total(self) -> float:
        return self.unit_price * self.quantity


@dataclasses.dataclass
class ProfitabilityData:
    project_name: str = ""
    region: str = ""
    business_item: str = ""
    business_description: str = ""
    base_year: int = 2025
    period_year: int = 3
    currency: str = "KRW"
    cost_items: List[CostItem] = dataclasses.field(default_factory=list)
    revenue_items: List[RevenueItem] = dataclasses.field(default_factory=list)
    optimistic_revenue_delta: float = 20.0
    optimistic_cost_delta: float = -10.0
    pessimistic_revenue_delta: float = -20.0
    pessimistic_cost_delta: float = 15.0
    exchange_rate_to_krw: float = 1300.0  # 1 외화 → 원 환산 환율
    discount_rate: float = 10.0        # 연간 할인율 (%)
    cost_growth_rate: float = 0.0      # 연간 비용 증가율 (%)
    ai_analysis: str = ""


class ProfitabilityCalculator:
    def __init__(self, data: ProfitabilityData):
        self.data = data

    def total_fixed_cost(self) -> float:
        return sum(
            item.amount for item in self.data.cost_items
            if item.category == "고정비" and item.period == "연별"
        ) * self.data.period_year + sum(
            item.amount for item in self.data.cost_items
            if item.category == "고정비" and item.period == "일회성"
        )

    def total_variable_cost(self) -> float:
        return sum(
            item.amount for item in self.data.cost_items
            if item.category == "변동비" and item.period == "연별"
        ) * self.data.period_year + sum(
            item.amount for item in self.data.cost_items
            if item.category == "변동비" and item.period == "일회성"
        )

    def total_cost(self) -> float:
        return self.total_fixed_cost() + self.total_variable_cost()

    def total_revenue(self) -> float:
        return sum(item.total for item in self.data.revenue_items)

    def net_profit(self) -> float:
        return self.total_revenue() - self.total_cost()

    def profit_margin(self) -> float:
        """순ROI (%)"""
        rev = self.total_revenue()
        if rev <= 0:
            return 0.0
        return (self.net_profit() / rev) * 100

    def breakeven_years(self) -> float:
        yearly_revenue = self.total_revenue() / max(self.data.period_year, 1)
        yearly_variable = sum(
            item.amount for item in self.data.cost_items
            if item.category == "변동비" and item.period == "연별"
        )
        yearly_contribution = yearly_revenue - yearly_variable
        if yearly_contribution <= 0:
            return float("inf")
        one_time = sum(
            item.amount for item in self.data.cost_items
            if item.period == "일회성"
        )
        return one_time / yearly_contribution if yearly_contribution > 0 else float("inf")

    def yearly_cashflow_simple(self) -> List[float]:
        yearly_revenue = self.total_revenue() / max(self.data.period_year, 1)
        yearly_cost = sum(item.amount for item in self.data.cost_items if item.period == "연별")
        initial = -sum(item.amount for item in self.data.cost_items if item.period == "일회성")
        flows = [initial]
        cumulative = initial
        for _ in range(self.data.period_year):
            yearly = yearly_revenue - yearly_cost
            cumulative += yearly
            flows.append(cumulative)
        return flows

    def yearly_cashflow(self) -> List[Dict]:
        """연도별 수익성 분석 (비용 증가율 적용)"""
        d = self.data
        total_years = d.period_year

        base_yearly_rev = sum(r.total for r in d.revenue_items) / max(d.period_year, 1)
        base_yearly_cost = sum(item.amount for item in d.cost_items if item.period == "연별")
        one_time_cost = sum(item.amount for item in d.cost_items if item.period == "일회성")
        cost_growth = d.cost_growth_rate / 100

        results: List[Dict] = []
        cumulative = -one_time_cost

        # 0년차: 일회성 비용
        results.append({
            "연도": f"{d.base_year}년 (0년차)",
            "수익": 0.0,
            "비용": one_time_cost,
            "순이익": -one_time_cost,
            "누적현금흐름": cumulative,
            "ROI": 0.0,
        })

        for yr in range(1, total_years + 1):
            rev = base_yearly_rev
            cost = base_yearly_cost * ((1 + cost_growth) ** (yr - 1))
            profit = rev - cost
            cumulative += profit
            margin = (profit / rev * 100) if rev > 0 else 0.0
            results.append({
                "연도": f"{d.base_year + yr}년 ({yr}년차)",
                "수익": rev,
                "비용": cost,
                "순이익": profit,
                "누적현금흐름": cumulative,
                "ROI": margin,
            })

        return results

    def scenario(self, rev_delta_pct: float, cost_delta_pct: float) -> dict:
        rev = self.total_revenue() * (1 + rev_delta_pct / 100)
        cost = self.total_cost() * (1 + cost_delta_pct / 100)
        profit = rev - cost
        margin = (profit / rev * 100) if rev > 0 else 0.0
        return {"revenue": rev, "cost": cost, "profit": profit, "roi": margin}

    def summary_dict(self) -> dict:
        return {
            "총 수익": self.total_revenue(),
            "총 비용": self.total_cost(),
            "고정비": self.total_fixed_cost(),
            "변동비": self.total_variable_cost(),
            "순이익": self.net_profit(),
            "ROI (%)": self.profit_margin(),
            "손익분기점 (년)": self.breakeven_years(),
        }

    def format_currency(self, amount: float) -> str:
        if self.data.currency == "KRW":
            return f"₩{amount:,.0f}"
        elif self.data.currency == "USD":
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {self.data.currency}"
