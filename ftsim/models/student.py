"""Student models for the food truck simulation."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StudentProfile:
    """Immutable student profile data loaded from CSVs."""

    student_id: int
    grade: int
    gender: str
    income_level: str  # Low, Medium, High
    q1_spend_on_drink: str
    q2_health_goal: str
    q3_metabolism: str
    q4_money_for_lunch: str
    q5_activity_level: str
    q6_healthy_importance: str
    q7_wants_sweet: str
    q8_lunch_choice: str

    # Drink preferences (ranks 1-5, lower is better)
    water_rank: int
    soda_rank: int
    juice_rank: int
    energy_drink_rank: int
    coffee_tea_rank: int

    # Assigned attributes
    has_car: bool


@dataclass
class StudentDailyState:
    """Daily randomized state for a student."""

    student_id: int
    available_money: float
    mood: str  # "healthy" or "junk"
    is_drowsy: bool

    # Decision tracking
    purchased_items: list = None
    total_spent: float = 0.0
    chose_school_lunch: bool = False
    chose_fast_food: bool = False
    loss_reason: Optional[str] = None
    purchased_from_truck: Optional[str] = None

    def __post_init__(self):
        if self.purchased_items is None:
            self.purchased_items = []

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "student_id": self.student_id,
            "available_money": self.available_money,
            "mood": self.mood,
            "is_drowsy": self.is_drowsy,
            "purchased_items": [item.name for item in self.purchased_items],
            "total_spent": self.total_spent,
            "chose_school_lunch": self.chose_school_lunch,
            "chose_fast_food": self.chose_fast_food,
            "loss_reason": self.loss_reason,
            "purchased_from_truck": self.purchased_from_truck,
        }
