"""Vendor models for the food truck simulation."""

import random
from dataclasses import dataclass, field
from typing import List

from .menu_item import MenuItem
from ..config import (
    SCHOOL_LUNCH_DAILY_FOOD_COUNT,
    SCHOOL_LUNCH_DAILY_DRINK_COUNT,
)

# Unlimited inventory sentinel
_UNLIMITED = 9999


@dataclass
class FoodTruck:
    """The player's food truck with inventory management."""

    name: str
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


# ---------------------------------------------------------------------------
# School Lunch
# ---------------------------------------------------------------------------

_SCHOOL_LUNCH_FOOD_POOL: List[MenuItem] = [
    MenuItem("Chicken Tenders", 3.50, 5, "food", "fried", "savory", False, _UNLIMITED, 450),
    MenuItem("Spaghetti w/ Meat Sauce", 3.00, 6, "food", "savory", "savory", False, _UNLIMITED, 500),
    MenuItem("Grilled Cheese", 2.50, 5, "food", "savory", "savory", False, _UNLIMITED, 400),
    MenuItem("Turkey Sandwich", 3.00, 7, "food", "healthy", "savory", False, _UNLIMITED, 350),
    MenuItem("Bean & Cheese Burrito", 3.00, 6, "food", "savory", "savory", False, _UNLIMITED, 480),
    MenuItem("Garden Salad", 2.00, 9, "food", "healthy", "savory", False, _UNLIMITED, 180),
    MenuItem("Fish Sticks", 3.00, 5, "food", "fried", "savory", False, _UNLIMITED, 400),
    MenuItem("Mac & Cheese", 2.50, 4, "food", "savory", "savory", False, _UNLIMITED, 450),
    MenuItem("Veggie Burger", 3.50, 7, "food", "healthy", "savory", False, _UNLIMITED, 320),
    MenuItem("Hamburger", 3.50, 5, "food", "fried", "savory", False, _UNLIMITED, 500),
]

_SCHOOL_LUNCH_DRINK_POOL: List[MenuItem] = [
    MenuItem("Chocolate Milk", 1.50, 5, "drink", "milk", "sweet", False, _UNLIMITED, 200),
    MenuItem("Apple Juice", 1.50, 7, "drink", "juice", "sweet", False, _UNLIMITED, 120),
    MenuItem("Fruit Punch", 1.50, 4, "drink", "juice", "sweet", False, _UNLIMITED, 150),
    MenuItem("Water", 0.00, 10, "drink", "water", "savory", False, _UNLIMITED, 0),
    MenuItem("Low-Fat Milk", 1.50, 8, "drink", "milk", "savory", False, _UNLIMITED, 110),
]


@dataclass
class SchoolLunch:
    """School lunch competitor — cheap, moderately healthy, daily rotating menu."""

    name: str = "School Lunch"
    daily_menu: List[MenuItem] = field(default_factory=list)

    def generate_daily_menu(self) -> None:
        """Pick random food + drink items from the pool for today's menu."""
        food_picks = random.sample(_SCHOOL_LUNCH_FOOD_POOL, SCHOOL_LUNCH_DAILY_FOOD_COUNT)
        drink_picks = random.sample(_SCHOOL_LUNCH_DRINK_POOL, SCHOOL_LUNCH_DAILY_DRINK_COUNT)
        self.daily_menu = food_picks + drink_picks

    # -- duck-typed interface matching FoodTruck for scoring --

    @property
    def menu(self) -> List[MenuItem]:
        return self.daily_menu

    def get_available_items(self) -> List[MenuItem]:
        return list(self.daily_menu)

    def get_available_food(self) -> List[MenuItem]:
        return [item for item in self.daily_menu if item.item_type == "food"]

    def get_available_drinks(self) -> List[MenuItem]:
        return [item for item in self.daily_menu if item.item_type == "drink"]

    def to_dict(self) -> dict:
        return {
            "daily_menu": [item.name for item in self.daily_menu],
        }


# ---------------------------------------------------------------------------
# Fast Food (Burger Joint)
# ---------------------------------------------------------------------------

_BURGER_JOINT_MENU: List[MenuItem] = [
    MenuItem("Cheeseburger", 6.00, 3, "food", "fried", "savory", False, _UNLIMITED, 550),
    MenuItem("Double Bacon Burger", 9.00, 2, "food", "fried", "savory", False, _UNLIMITED, 900),
    MenuItem("Chicken Nuggets (10pc)", 7.00, 3, "food", "fried", "savory", False, _UNLIMITED, 480),
    MenuItem("Large Fries", 5.00, 2, "food", "fried", "savory", False, _UNLIMITED, 500),
    MenuItem("Hot Dog", 5.00, 3, "food", "fried", "savory", False, _UNLIMITED, 400),
    MenuItem("Large Soda", 3.00, 1, "drink", "soda", "sweet", False, _UNLIMITED, 250),
    MenuItem("Chocolate Shake", 6.00, 2, "drink", "milk", "sweet", False, _UNLIMITED, 700),
    MenuItem("Sweet Tea", 3.00, 2, "drink", "juice", "sweet", False, _UNLIMITED, 180),
]


@dataclass
class FastFood:
    """Burger joint competitor — expensive, junky, requires car access."""

    name: str = "Burger Joint"

    # -- duck-typed interface matching FoodTruck for scoring --

    @property
    def menu(self) -> List[MenuItem]:
        return _BURGER_JOINT_MENU

    def get_available_items(self) -> List[MenuItem]:
        return list(_BURGER_JOINT_MENU)

    def get_available_food(self) -> List[MenuItem]:
        return [item for item in _BURGER_JOINT_MENU if item.item_type == "food"]

    def get_available_drinks(self) -> List[MenuItem]:
        return [item for item in _BURGER_JOINT_MENU if item.item_type == "drink"]

    def to_dict(self) -> dict:
        return {
            "menu": [item.name for item in _BURGER_JOINT_MENU],
        }
