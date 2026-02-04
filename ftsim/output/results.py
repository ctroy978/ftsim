"""Result dataclasses for the food truck simulation."""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class DailyResult:
    """Results for a single day of simulation."""

    day: int
    revenue: float
    customers: int
    items_sold: Dict[str, int]  # item_name -> count
    stockouts: Dict[str, int]  # item_name -> times sold out
    losses_by_reason: Dict[str, int]  # reason -> count
    total_students: int
    school_lunch_price: float

    # Optional detailed state for export
    student_states: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "day": self.day,
            "revenue": round(self.revenue, 2),
            "customers": self.customers,
            "items_sold": self.items_sold,
            "stockouts": self.stockouts,
            "losses_by_reason": self.losses_by_reason,
            "total_students": self.total_students,
            "school_lunch_price": round(self.school_lunch_price, 2),
            "student_states": self.student_states,
        }


@dataclass
class AggregateResult:
    """Aggregated results across all simulation days."""

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
