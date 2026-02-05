"""Data loading utilities for the food truck simulation."""

import csv
import json
import random
from pathlib import Path
from typing import List, Dict, Any, NamedTuple

from ..models.student import StudentProfile
from ..models.menu_item import MenuItem
from ..config import (
    HAS_CAR_PERCENTAGE,
    FOOD_CATEGORIES,
    DRINK_CATEGORIES,
    VALID_SUB_TYPES,
    ITEM_TYPE_FOOD,
    ITEM_TYPE_DRINK,
)


def _parse_q4_money(q4_value: str) -> str:
    """Normalize Q4_MoneyForLunch values."""
    q4_lower = q4_value.lower()
    if "less than" in q4_lower or "low" in q4_lower:
        return "Less than $7"
    elif "more than" in q4_lower or "high" in q4_lower:
        return "More than $10"
    else:
        return "$7-$10"


def _parse_q6_healthy(q6_value: str) -> str:
    """Normalize Q6_HealthyImportance values."""
    q6_lower = q6_value.lower()
    if "very important" in q6_lower:
        return "Very important - I always try to choose nutritious options"
    elif "somewhat" in q6_lower:
        return "Somewhat important - I try to balance healthy and tasty"
    else:
        return "Not really important - I just eat what tastes good"


def _parse_q7_sweet(q7_value: str) -> str:
    """Normalize Q7_WantsSweet values."""
    q7_lower = q7_value.lower()
    if "yes" in q7_lower or "always" in q7_lower:
        return "Yes, I often crave something sweet"
    elif "sometimes" in q7_lower:
        return "Sometimes"
    elif "rarely" in q7_lower:
        return "Rarely"
    else:
        return "No, I prefer savory"


def _parse_q5_activity(q5_value: str) -> str:
    """Normalize Q5_ActivityLevel values."""
    q5_lower = q5_value.lower()
    if "very active" in q5_lower or "sports team" in q5_lower:
        return "Very active (exercise daily)"
    elif "active" in q5_lower or "sometimes" in q5_lower or "somewhat" in q5_lower:
        return "Active (exercise 3-4 times a week)"
    else:
        return "Not very active"


def _parse_q3_metabolism(q3_value: str) -> str:
    """Normalize Q3_Metabolism values."""
    q3_lower = q3_value.lower()
    if "fast" in q3_lower or "eat a lot" in q3_lower or "hungry" in q3_lower:
        return "Fast - I can eat a lot without gaining weight"
    elif "slow" in q3_lower or "full" in q3_lower:
        return "Slow - I get full easily"
    else:
        return "Average"


def _parse_q2_health_goal(q2_value: str) -> str:
    """Normalize Q2_HealthGoal values."""
    q2_lower = q2_value.lower()
    if "lose" in q2_lower:
        return "Lose weight"
    elif "gain" in q2_lower or "muscle" in q2_lower or "stronger" in q2_lower:
        return "Gain weight/muscle"
    elif "maintain" in q2_lower:
        return "Maintain weight"
    else:
        return "Not focused on weight"


def _parse_q1_spend(q1_value: str) -> str:
    """Normalize Q1_SpendOnDrink values."""
    q1_lower = q1_value.lower()
    if "$4" in q1_lower or "more" in q1_lower:
        return "More than $5"
    elif "$3" in q1_lower:
        return "$3-$5"
    elif "$2" in q1_lower:
        return "$2-$3"
    else:
        return "Less than $2"


def _drink_to_rank(drink_name: str) -> Dict[str, int]:
    """Map drink name to drink category for ranking."""
    drink_lower = drink_name.lower()

    categories = {
        "water": ["water", "sparkling water"],
        "soda": ["pepsi", "coca-cola", "coke", "dr pepper", "sprite", "fanta", "mountain dew"],
        "juice": ["juice", "lemonade", "tea"],
        "energy_drink": ["red bull", "monster", "rockstar", "bang", "energy"],
        "coffee_tea": ["coffee", "iced coffee", "milk"],
    }

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in drink_lower:
                return category

    return "soda"  # Default


def load_students(
    food_csv_path: str,
    drink_csv_path: str,
    random_seed: int = None,
) -> List[StudentProfile]:
    """Load and merge student data from CSV files.

    Args:
        food_csv_path: Path to student_food.csv
        drink_csv_path: Path to drink_preferences_survey_500.csv
        random_seed: Optional seed for reproducibility

    Returns:
        List of 1000 StudentProfile objects
    """
    if random_seed is not None:
        random.seed(random_seed)

    # Load food preferences (1000 students)
    food_data = {}
    with open(food_csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            student_id = int(row["StudentID"])
            food_data[student_id] = row

    # Load drink preferences (500 students)
    drink_data_raw = []
    with open(drink_csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            drink_data_raw.append(row)

    # Double drink data to match 1000 students
    drink_data = {}
    for i, row in enumerate(drink_data_raw):
        drink_data[i + 1] = row
    for i, row in enumerate(drink_data_raw):
        drink_data[i + 501] = row

    # Assign has_car randomly to 20% of students
    all_student_ids = list(food_data.keys())
    num_with_cars = int(len(all_student_ids) * HAS_CAR_PERCENTAGE)
    students_with_cars = set(random.sample(all_student_ids, num_with_cars))

    # Create StudentProfile objects
    students = []
    for student_id, food_row in food_data.items():
        drink_row = drink_data.get(student_id, {})

        # Parse drink rankings from top 3 drinks
        drink_ranks = {"water": 5, "soda": 5, "juice": 5, "energy_drink": 5, "coffee_tea": 5}
        for rank_idx, rank_col in enumerate(["Rank1_Drink", "Rank2_Drink", "Rank3_Drink"], 1):
            if rank_col in drink_row and drink_row[rank_col]:
                category = _drink_to_rank(drink_row[rank_col])
                if drink_ranks[category] == 5:  # Only update if not already ranked
                    drink_ranks[category] = rank_idx

        profile = StudentProfile(
            student_id=student_id,
            grade=random.randint(9, 12),  # Assign random grade if not in data
            gender=random.choice(["M", "F"]),  # Assign random if not in data
            income_level=food_row.get("IncomeLevel", "Medium"),
            q1_spend_on_drink=_parse_q1_spend(drink_row.get("Q1_SpendOnDrink", "About $2")),
            q2_health_goal=_parse_q2_health_goal(food_row.get("Q2_HealthGoal", "")),
            q3_metabolism=_parse_q3_metabolism(food_row.get("Q3_Metabolism", "")),
            q4_money_for_lunch=_parse_q4_money(food_row.get("Q4_MoneyForLunch", "")),
            q5_activity_level=_parse_q5_activity(food_row.get("Q5_ActivityLevel", "")),
            q6_healthy_importance=_parse_q6_healthy(food_row.get("Q6_HealthyImportance", "")),
            q7_wants_sweet=_parse_q7_sweet(food_row.get("Q7_WantsSweet", "")),
            q8_lunch_choice=food_row.get("Q8_LunchChoice", ""),
            water_rank=drink_ranks["water"],
            soda_rank=drink_ranks["soda"],
            juice_rank=drink_ranks["juice"],
            energy_drink_rank=drink_ranks["energy_drink"],
            coffee_tea_rank=drink_ranks["coffee_tea"],
            has_car=student_id in students_with_cars,
        )
        students.append(profile)

    return students


class MenuData(NamedTuple):
    """Container for loaded menu data."""
    name: str
    items: List[MenuItem]


def load_menu(menu_path: str) -> MenuData:
    """Load menu from JSON or YAML file.

    All fields are required. See README.md for field documentation.

    Args:
        menu_path: Path to menu file (JSON or YAML)

    Returns:
        MenuData named tuple with (name, items)

    Raises:
        ValueError: If required fields are missing or have invalid values
    """
    path = Path(menu_path)

    with open(path, encoding="utf-8") as f:
        if path.suffix.lower() in (".yaml", ".yml"):
            try:
                import yaml
                data = yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML is required to load YAML files. Install with: pip install pyyaml")
        else:
            data = json.load(f)

    # Extract company name
    company_name = data.get("name")
    if not company_name:
        raise ValueError("Menu file must include a 'name' field for the company name")
    if not isinstance(company_name, str) or not company_name.strip():
        raise ValueError("Menu 'name' field must be a non-empty string")
    company_name = company_name.strip()

    items = []
    required_fields = [
        "name",
        "price",
        "health_rating",
        "type",
        "category",
        "sub_type",
        "energy_boost",
        "inventory_per_day",
        "calories",
    ]

    for idx, item_data in enumerate(data.get("items", [])):
        item_name = item_data.get("name", f"Item {idx + 1}")

        # Validate all required fields are present
        for field in required_fields:
            if field not in item_data:
                raise ValueError(f"Menu item '{item_name}' missing required field: {field}")

        # Validate type
        item_type = item_data["type"]
        if item_type not in (ITEM_TYPE_FOOD, ITEM_TYPE_DRINK):
            raise ValueError(
                f"Menu item '{item_name}' has invalid type '{item_type}'. "
                f"Must be '{ITEM_TYPE_FOOD}' or '{ITEM_TYPE_DRINK}'"
            )

        # Validate category based on type
        category = item_data["category"]
        if item_type == ITEM_TYPE_FOOD:
            if category not in FOOD_CATEGORIES:
                raise ValueError(
                    f"Menu item '{item_name}' has invalid food category '{category}'. "
                    f"Must be one of: {', '.join(sorted(FOOD_CATEGORIES))}"
                )
        else:
            if category not in DRINK_CATEGORIES:
                raise ValueError(
                    f"Menu item '{item_name}' has invalid drink category '{category}'. "
                    f"Must be one of: {', '.join(sorted(DRINK_CATEGORIES))}"
                )

        # Validate sub_type
        sub_type = item_data["sub_type"]
        if sub_type not in VALID_SUB_TYPES:
            raise ValueError(
                f"Menu item '{item_name}' has invalid sub_type '{sub_type}'. "
                f"Must be one of: {', '.join(sorted(VALID_SUB_TYPES))}"
            )

        # Validate health_rating range
        health_rating = int(item_data["health_rating"])
        if not 1 <= health_rating <= 10:
            raise ValueError(
                f"Menu item '{item_name}' has invalid health_rating {health_rating}. "
                "Must be between 1 and 10"
            )

        # Validate price is positive
        price = float(item_data["price"])
        if price <= 0:
            raise ValueError(f"Menu item '{item_name}' has invalid price {price}. Must be positive")

        # Validate inventory is positive
        inventory = int(item_data["inventory_per_day"])
        if inventory <= 0:
            raise ValueError(
                f"Menu item '{item_name}' has invalid inventory_per_day {inventory}. Must be positive"
            )

        # Validate calories is non-negative
        calories = int(item_data["calories"])
        if calories < 0:
            raise ValueError(f"Menu item '{item_name}' has invalid calories {calories}. Must be non-negative")

        item = MenuItem(
            name=item_data["name"],
            price=price,
            health_rating=health_rating,
            item_type=item_type,
            category=category,
            sub_type=sub_type,
            energy_boost=bool(item_data["energy_boost"]),
            inventory_per_day=inventory,
            calories=calories,
        )
        items.append(item)

    if not items:
        raise ValueError("Menu file contains no items")

    return MenuData(name=company_name, items=items)
