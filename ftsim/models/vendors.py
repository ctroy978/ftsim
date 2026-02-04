"""Vendor models for the food truck simulation."""

import random
from dataclasses import dataclass, field
from typing import List

from .menu_item import MenuItem
from ..config import (
    SCHOOL_LUNCH_MIN_PRICE,
    SCHOOL_LUNCH_MAX_PRICE,
    SCHOOL_LUNCH_HEALTH_RATING,
    FAST_FOOD_PRICE_MULTIPLIER_MIN,
    FAST_FOOD_PRICE_MULTIPLIER_MAX,
)


@dataclass
class FoodTruck:
    """The player's food truck with inventory management."""

    menu: List[MenuItem] = field(default_factory=list)

    def reset_inventory(self) -> None:
        """Reset all menu items to daily inventory levels."""
        for item in self.menu:
            item.reset_inventory()

    def get_available_items(self) -> List[MenuItem]:
        """Get list of items currently in stock."""
        return [item for item in self.menu if item.is_available()]

    def get_available_food(self) -> List[MenuItem]:
        """Get available food items."""
        return [item for item in self.get_available_items() if item.item_type == "food"]

    def get_available_drinks(self) -> List[MenuItem]:
        """Get available drink items."""
        return [item for item in self.get_available_items() if item.item_type == "drink"]

    def sell_item(self, item: MenuItem) -> bool:
        """Attempt to sell an item. Returns True if successful."""
        return item.sell_one()


@dataclass
class SchoolLunch:
    """School lunch competitor - cheap and moderately healthy."""

    price: float = field(default=0.0)
    health_rating: int = field(default=SCHOOL_LUNCH_HEALTH_RATING)

    def generate_daily_price(self) -> None:
        """Generate random daily price within range."""
        self.price = random.uniform(SCHOOL_LUNCH_MIN_PRICE, SCHOOL_LUNCH_MAX_PRICE)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "price": self.price,
            "health_rating": self.health_rating,
        }


@dataclass
class FastFood:
    """Fast food competitor - expensive, requires car access."""

    base_price: float = 8.00  # Base price for fast food meal
    health_rating: int = 3  # Generally unhealthy

    def get_price(self) -> float:
        """Get price with random multiplier."""
        multiplier = random.uniform(
            FAST_FOOD_PRICE_MULTIPLIER_MIN, FAST_FOOD_PRICE_MULTIPLIER_MAX
        )
        return self.base_price * multiplier

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "base_price": self.base_price,
            "health_rating": self.health_rating,
        }
