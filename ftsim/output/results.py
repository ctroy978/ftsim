"""Result dataclasses for the food truck simulation."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class TruckDailyResult:
    """Results for a single truck for a single day."""

    truck_name: str
    revenue: float
    customers: int
    items_sold: Dict[str, int]  # item_name -> count
    stockouts: Dict[str, int]  # item_name -> sold out (0 or 1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "truck_name": self.truck_name,
            "revenue": round(self.revenue, 2),
            "customers": self.customers,
            "items_sold": self.items_sold,
            "stockouts": self.stockouts,
        }


@dataclass
class DailyResult:
    """Results for a single day of simulation."""

    day: int
    truck_results: Dict[str, TruckDailyResult]  # keyed by truck name
    losses_by_reason: Dict[str, int]  # reason -> count
    total_students: int
    school_lunch_menu: List[str]

    # Optional detailed state for export
    student_states: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def revenue(self) -> float:
        """Total revenue across all trucks."""
        return sum(tr.revenue for tr in self.truck_results.values())

    @property
    def customers(self) -> int:
        """Total customers across all trucks."""
        return sum(tr.customers for tr in self.truck_results.values())

    @property
    def items_sold(self) -> Dict[str, int]:
        """Combined items sold across all trucks."""
        combined: Dict[str, int] = {}
        for tr in self.truck_results.values():
            for item_name, count in tr.items_sold.items():
                combined[item_name] = combined.get(item_name, 0) + count
        return combined

    @property
    def stockouts(self) -> Dict[str, int]:
        """Combined stockouts across all trucks."""
        combined: Dict[str, int] = {}
        for tr in self.truck_results.values():
            for item_name, count in tr.stockouts.items():
                combined[item_name] = combined.get(item_name, 0) + count
        return combined

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "day": self.day,
            "truck_results": {name: tr.to_dict() for name, tr in self.truck_results.items()},
            "total_revenue": round(self.revenue, 2),
            "total_customers": self.customers,
            "losses_by_reason": self.losses_by_reason,
            "total_students": self.total_students,
            "school_lunch_menu": self.school_lunch_menu,
            "student_states": self.student_states,
        }


@dataclass
class TruckAggregateResult:
    """Aggregated results for a single truck across all days."""

    truck_name: str
    total_revenue: float
    total_customers: int
    total_items_sold: Dict[str, int]
    total_stockouts: Dict[str, int]  # item_name -> days sold out
    avg_daily_revenue: float
    avg_daily_customers: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "truck_name": self.truck_name,
            "total_revenue": round(self.total_revenue, 2),
            "total_customers": self.total_customers,
            "total_items_sold": self.total_items_sold,
            "total_stockouts": self.total_stockouts,
            "avg_daily_revenue": round(self.avg_daily_revenue, 2),
            "avg_daily_customers": round(self.avg_daily_customers, 1),
        }


@dataclass
class CompetitionAggregateResult:
    """Aggregated results for head-to-head competition."""

    total_days: int
    truck_results: Dict[str, TruckAggregateResult]  # keyed by truck name
    total_losses_by_reason: Dict[str, int]
    total_students_served: int
    winner: str  # truck name with highest revenue

    # All daily results for detailed analysis
    daily_results: List[DailyResult] = field(default_factory=list)

    @property
    def total_revenue(self) -> float:
        """Total revenue across all trucks."""
        return sum(tr.total_revenue for tr in self.truck_results.values())

    @property
    def total_customers(self) -> int:
        """Total customers across all trucks."""
        return sum(tr.total_customers for tr in self.truck_results.values())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "summary": {
                "total_days": self.total_days,
                "total_revenue": round(self.total_revenue, 2),
                "total_customers": self.total_customers,
                "total_losses_by_reason": self.total_losses_by_reason,
                "total_students_served": self.total_students_served,
                "winner": self.winner,
            },
            "truck_results": {name: tr.to_dict() for name, tr in self.truck_results.items()},
            "daily_results": [dr.to_dict() for dr in self.daily_results],
        }


@dataclass
class AggregateResult:
    """Aggregated results across all simulation days (legacy single-truck)."""

    total_days: int
    total_revenue: float
    total_customers: int
    total_items_sold: Dict[str, int]
    total_stockouts: Dict[str, int]
    total_losses_by_reason: Dict[str, int]
    total_students_served: int

    # Averages
    avg_daily_revenue: float
    avg_daily_customers: float
    avg_items_per_customer: float
    customer_rate: float  # percentage of students who bought from truck

    # All daily results for detailed analysis
    daily_results: List[DailyResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "summary": {
                "total_days": self.total_days,
                "total_revenue": round(self.total_revenue, 2),
                "total_customers": self.total_customers,
                "total_items_sold": self.total_items_sold,
                "total_stockouts": self.total_stockouts,
                "total_losses_by_reason": self.total_losses_by_reason,
                "total_students_served": self.total_students_served,
            },
            "averages": {
                "daily_revenue": round(self.avg_daily_revenue, 2),
                "daily_customers": round(self.avg_daily_customers, 1),
                "items_per_customer": round(self.avg_items_per_customer, 2),
                "customer_rate_percent": round(self.customer_rate * 100, 1),
            },
            "daily_results": [dr.to_dict() for dr in self.daily_results],
        }
