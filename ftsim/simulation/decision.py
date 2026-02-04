"""Student decision logic for the food truck simulation."""

import random
from typing import List, Optional, Tuple

from ..models.menu_item import MenuItem
from ..models.student import StudentProfile, StudentDailyState
from ..models.vendors import FoodTruck, SchoolLunch
from ..scoring.scorer import score_item, score_school_lunch
from ..config import (
    FAST_FOOD_CHANCE,
    LOSS_REASON_SCHOOL_LUNCH,
    LOSS_REASON_PRICE,
    LOSS_REASON_STOCKOUT,
    LOSS_REASON_FASTFOOD,
    ITEM_TYPE_FOOD,
    ITEM_TYPE_DRINK,
)


def _check_fast_food(profile: StudentProfile, state: StudentDailyState) -> bool:
    """Check if student chooses fast food.

    Returns:
        True if student chooses fast food
    """
    if profile.has_car and state.mood == "junk":
        return random.random() < FAST_FOOD_CHANCE
    return False


def _find_best_items(
    truck: FoodTruck,
    profile: StudentProfile,
    state: StudentDailyState,
) -> Tuple[Optional[MenuItem], Optional[MenuItem], float]:
    """Find best food and drink items for student.

    Returns:
        Tuple of (best_food, best_drink, combined_score)
    """
    available_food = truck.get_available_food()
    available_drinks = truck.get_available_drinks()

    best_food = None
    best_food_score = 0.0

    best_drink = None
    best_drink_score = 0.0

    # Score food items
    for item in available_food:
        score = score_item(item, profile, state)
        if score > best_food_score:
            best_food_score = score
            best_food = item

    # Score drink items
    for item in available_drinks:
        score = score_item(item, profile, state)
        if score > best_drink_score:
            best_drink_score = score
            best_drink = item

    # Combined score is the max of food score and (food + drink) if both affordable
    combined_score = best_food_score
    if best_food and best_drink:
        if best_food.price + best_drink.price <= state.available_money:
            combined_score = max(best_food_score, (best_food_score + best_drink_score) / 1.5)

    return best_food, best_drink, combined_score


def make_decision(
    profile: StudentProfile,
    state: StudentDailyState,
    truck: FoodTruck,
    school_lunch: SchoolLunch,
) -> None:
    """Process a student's lunch decision.

    Modifies state in place to record the decision outcome.

    Args:
        profile: Student's permanent profile
        state: Student's daily state (will be modified)
        truck: The food truck
        school_lunch: School lunch competitor
    """
    # Check for fast food first
    if _check_fast_food(profile, state):
        state.chose_fast_food = True
        state.loss_reason = LOSS_REASON_FASTFOOD
        return

    # Find best truck items
    best_food, best_drink, truck_score = _find_best_items(truck, profile, state)

    # Get school lunch score
    school_score = score_school_lunch(profile, state, school_lunch.price)

    # Check if any truck items are available
    all_available = truck.get_available_items()
    if not all_available:
        state.chose_school_lunch = True
        state.loss_reason = LOSS_REASON_STOCKOUT
        return

    # Check if any items are affordable
    affordable_items = [item for item in all_available if item.price <= state.available_money]
    if not affordable_items:
        state.chose_school_lunch = True
        state.loss_reason = LOSS_REASON_PRICE
        return

    # Compare scores
    if truck_score > school_score and best_food:
        # Buy from truck
        remaining_money = state.available_money

        # Try to buy food
        if best_food and best_food.price <= remaining_money:
            if truck.sell_item(best_food):
                state.purchased_items.append(best_food)
                state.total_spent += best_food.price
                remaining_money -= best_food.price

        # Try to also buy drink if affordable
        if best_drink and best_drink.price <= remaining_money:
            if truck.sell_item(best_drink):
                state.purchased_items.append(best_drink)
                state.total_spent += best_drink.price

        # Check if purchase was successful
        if not state.purchased_items:
            # Stockout occurred during purchase
            state.chose_school_lunch = True
            state.loss_reason = LOSS_REASON_STOCKOUT
    else:
        # School lunch wins
        state.chose_school_lunch = True
        state.loss_reason = LOSS_REASON_SCHOOL_LUNCH
