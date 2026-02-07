"""Student decision logic for the food truck simulation."""

from typing import List, Optional, Union
from dataclasses import dataclass

from ..models.menu_item import MenuItem
from ..models.student import StudentProfile, StudentDailyState
from ..models.vendors import FoodTruck, SchoolLunch, FastFood
from ..scoring.scorer import score_item
from ..config import (
    LOSS_REASON_SCHOOL_LUNCH,
    LOSS_REASON_PRICE,
    LOSS_REASON_STOCKOUT,
    LOSS_REASON_FASTFOOD,
    ITEM_TYPE_FOOD,
    ITEM_TYPE_DRINK,
    PENALTY_NO_DRINK,
)

# Any vendor type that exposes the duck-typed menu interface
Vendor = Union[FoodTruck, SchoolLunch, FastFood]


@dataclass
class TruckOption:
    """Best food/drink option from a specific vendor."""
    truck: Vendor
    best_food: Optional[MenuItem]
    best_drink: Optional[MenuItem]
    combined_score: float


def _find_best_items_for_truck(
    truck: Vendor,
    profile: StudentProfile,
    state: StudentDailyState,
) -> TruckOption:
    """Find best food and drink items for student from a specific vendor.

    Returns:
        TruckOption with (truck, best_food, best_drink, combined_score)
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

    # Combined score considers whether student can afford food + drink
    combined_score = best_food_score
    if best_food and best_drink:
        if best_food.price + best_drink.price <= state.available_money:
            # Can afford both - use combined score
            combined_score = max(best_food_score, (best_food_score + best_drink_score) / 1.5)
        else:
            # Can afford food but not drink - penalty for incomplete meal
            combined_score = best_food_score * PENALTY_NO_DRINK

    return TruckOption(
        truck=truck,
        best_food=best_food,
        best_drink=best_drink,
        combined_score=combined_score,
    )


def _find_best_items(
    trucks: List[FoodTruck],
    profile: StudentProfile,
    state: StudentDailyState,
) -> Optional[TruckOption]:
    """Find best food and drink items for student across all trucks.

    Returns:
        TruckOption for the best truck, or None if no options available
    """
    best_option: Optional[TruckOption] = None

    for truck in trucks:
        option = _find_best_items_for_truck(truck, profile, state)
        if option.best_food is not None:
            if best_option is None or option.combined_score > best_option.combined_score:
                best_option = option

    return best_option


def make_decision(
    profile: StudentProfile,
    state: StudentDailyState,
    trucks: List[FoodTruck],
    school_lunch: SchoolLunch,
    fast_food: FastFood,
) -> None:
    """Process a student's lunch decision.

    Scores every vendor's menu through the same scoring system and picks the
    vendor with the highest combined score.

    Modifies state in place to record the decision outcome.
    """
    # ---- Collect candidate options from all vendors ----

    # Food trucks
    best_truck = _find_best_items(trucks, profile, state)

    # School lunch (always available)
    school_option = _find_best_items_for_truck(school_lunch, profile, state)

    # Burger joint (only if student has car)
    burger_option: Optional[TruckOption] = None
    if profile.has_car:
        burger_option = _find_best_items_for_truck(fast_food, profile, state)

    # ---- Check if trucks have any stock at all ----
    all_available: List[MenuItem] = []
    for truck in trucks:
        all_available.extend(truck.get_available_items())

    # ---- Pick the best overall vendor ----
    candidates: List[TruckOption] = []
    if best_truck and best_truck.best_food:
        candidates.append(best_truck)
    if school_option and school_option.best_food:
        candidates.append(school_option)
    if burger_option and burger_option.best_food:
        candidates.append(burger_option)

    if not candidates:
        # Nothing available anywhere — default to school lunch loss
        state.chose_school_lunch = True
        state.loss_reason = LOSS_REASON_STOCKOUT
        return

    winner = max(candidates, key=lambda c: c.combined_score)

    # ---- Act on the winner ----

    if isinstance(winner.truck, SchoolLunch):
        state.chose_school_lunch = True
        state.loss_reason = LOSS_REASON_SCHOOL_LUNCH
        return

    if isinstance(winner.truck, FastFood):
        state.chose_fast_food = True
        state.loss_reason = LOSS_REASON_FASTFOOD
        return

    # Winner is a food truck — attempt purchase
    truck = winner.truck
    best_food = winner.best_food
    best_drink = winner.best_drink
    remaining_money = state.available_money

    # Try to buy food
    if best_food and best_food.price <= remaining_money:
        if truck.sell_item(best_food):
            state.purchased_items.append(best_food)
            state.total_spent += best_food.price
            state.purchased_from_truck = truck.name
            remaining_money -= best_food.price

    # Try to also buy drink if affordable (from same truck)
    if best_drink and best_drink.price <= remaining_money:
        if truck.sell_item(best_drink):
            state.purchased_items.append(best_drink)
            state.total_spent += best_drink.price

    # Check if purchase was successful
    if not state.purchased_items:
        # Stockout occurred during purchase attempt
        state.chose_school_lunch = True
        state.loss_reason = LOSS_REASON_STOCKOUT
        state.purchased_from_truck = None
