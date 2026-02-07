"""Scoring logic for student purchase decisions."""

from rapidfuzz import fuzz

from ..models.menu_item import MenuItem
from ..models.student import StudentProfile, StudentDailyState
from ..config import (
    WEIGHT_PREFERENCE,
    WEIGHT_AFFORDABILITY,
    WEIGHT_MOOD_HEALTH,
    BONUS_FUZZY_MATCH_HIGH,
    BONUS_FUZZY_MATCH_MEDIUM,
    BONUS_SWEET,
    BONUS_SAVORY,
    BONUS_ENERGY,
    BONUS_HIGH_CALORIE,
    BONUS_CATEGORY_MATCH,
    FUZZY_THRESHOLD_HIGH,
    FUZZY_THRESHOLD_MEDIUM,
    HIGH_CALORIE_THRESHOLD,
    SWEET_PREFERENCE_VALUES,
    HIGH_ACTIVITY_LEVELS,
    HIGH_METABOLISM_VALUES,
    ITEM_TYPE_DRINK,
)


def _fuzzy_match_score(item_name: str, favorite: str) -> int:
    """Calculate fuzzy match score between item name and favorite food.

    Uses multiple fuzzy matching strategies and returns the best score.

    Args:
        item_name: The menu item name
        favorite: The student's favorite food (Q8_LunchChoice)

    Returns:
        Fuzzy match score 0-100
    """
    item_lower = item_name.lower()
    favorite_lower = favorite.lower()

    # Try multiple matching strategies and take the best
    scores = [
        fuzz.ratio(item_lower, favorite_lower),
        fuzz.partial_ratio(item_lower, favorite_lower),
        fuzz.token_sort_ratio(item_lower, favorite_lower),
        fuzz.token_set_ratio(item_lower, favorite_lower),
    ]

    return max(scores)


def _get_drink_category_rank(item: MenuItem, profile: StudentProfile) -> int:
    """Get student's rank for this drink category.

    Args:
        item: The drink menu item
        profile: Student profile with drink rankings

    Returns:
        Rank 1-5 (1 is best, 5 is worst/unranked)
    """
    category = item.category.lower()

    category_to_rank = {
        "energy": profile.energy_drink_rank,
        "soda": profile.soda_rank,
        "juice": profile.juice_rank,
        "water": profile.water_rank,
        "milk": profile.coffee_tea_rank,  # Grouped with coffee/tea in survey
        "coffee": profile.coffee_tea_rank,
    }

    return category_to_rank.get(category, 5)


def _score_preference(
    item: MenuItem,
    profile: StudentProfile,
) -> tuple[float, int]:
    """Score item based on preference match.

    Args:
        item: The menu item to score
        profile: Student profile

    Returns:
        Tuple of (preference_score 0-1, fuzzy_match_score 0-100)
    """
    # Get fuzzy match score against favorite food
    fuzzy_score = _fuzzy_match_score(item.name, profile.q8_lunch_choice)

    # High fuzzy match means strong preference
    if fuzzy_score >= FUZZY_THRESHOLD_HIGH:
        return 1.0, fuzzy_score
    elif fuzzy_score >= FUZZY_THRESHOLD_MEDIUM:
        return 0.85, fuzzy_score

    # For drinks, use category-based ranking
    if item.item_type == ITEM_TYPE_DRINK:
        rank = _get_drink_category_rank(item, profile)
        # Convert rank (1-5) to score (1.0 - 0.2)
        drink_score = (6 - rank) / 5.0
        return max(drink_score, 0.3), fuzzy_score

    # For food, check category alignment with favorite food
    favorite_lower = profile.q8_lunch_choice.lower()
    category = item.category.lower()

    # Category matching based on favorite food characteristics
    if category == "healthy":
        # Healthy items match healthy-sounding favorites
        healthy_keywords = ["salad", "veggie", "fruit", "yogurt", "grilled", "wrap"]
        if any(kw in favorite_lower for kw in healthy_keywords):
            return 0.75, fuzzy_score

    elif category == "fried":
        # Fried items match indulgent favorites
        fried_keywords = ["fries", "burger", "tenders", "rings", "corn dog", "nachos", "cheese"]
        if any(kw in favorite_lower for kw in fried_keywords):
            return 0.75, fuzzy_score

    elif category == "sweet":
        # Sweet items match dessert favorites
        sweet_keywords = ["brownie", "cookie", "ice cream", "churro", "cinnamon", "funnel", "parfait"]
        if any(kw in favorite_lower for kw in sweet_keywords):
            return 0.75, fuzzy_score

    elif category == "savory":
        # Savory items match main dish favorites
        savory_keywords = ["bowl", "wrap", "sandwich", "burrito", "chicken", "beef", "pork", "tacos"]
        if any(kw in favorite_lower for kw in savory_keywords):
            return 0.70, fuzzy_score

    elif category == "snack":
        # Snacks have moderate appeal
        return 0.50, fuzzy_score

    # Default moderate preference
    return 0.40, fuzzy_score


def _score_affordability(
    item: MenuItem,
    state: StudentDailyState,
) -> float:
    """Score item based on affordability.

    Returns:
        Score from 0-1, where 1 means very affordable
    """
    if item.price > state.available_money:
        return 0.0  # Can't afford

    # Score based on what fraction of budget remains after purchase
    remaining_fraction = (state.available_money - item.price) / state.available_money
    # Boost for items that leave more budget
    return 0.3 + (remaining_fraction * 0.7)


def _score_mood_health(
    item: MenuItem,
    state: StudentDailyState,
) -> float:
    """Score item based on mood/health alignment.

    Returns:
        Score from 0-1
    """
    # Normalize health rating to 0-1
    health_score = item.health_rating / 10.0

    if state.mood == "healthy":
        # Healthy mood prefers high health rating
        return health_score
    else:
        # Junk mood prefers low health rating (inverted)
        return 1.0 - health_score


def _calculate_bonuses(
    item: MenuItem,
    profile: StudentProfile,
    state: StudentDailyState,
    fuzzy_score: int,
) -> float:
    """Calculate multiplicative bonuses.

    Args:
        item: The menu item
        profile: Student profile
        state: Daily state
        fuzzy_score: Fuzzy match score against favorite (0-100)

    Returns:
        Bonus multiplier (>= 1.0)
    """
    bonus = 1.0

    # Fuzzy match bonuses (significant for matching favorite food)
    if fuzzy_score >= FUZZY_THRESHOLD_HIGH:
        bonus *= BONUS_FUZZY_MATCH_HIGH  # +100% for high confidence match
    elif fuzzy_score >= FUZZY_THRESHOLD_MEDIUM:
        bonus *= BONUS_FUZZY_MATCH_MEDIUM  # +50% for medium confidence match

    # Sweet/savory preference bonuses
    wants_sweet = SWEET_PREFERENCE_VALUES.get(profile.q7_wants_sweet, False)
    prefers_savory = profile.q7_wants_sweet == "No, I prefer savory"

    if wants_sweet and item.sub_type == "sweet":
        bonus *= BONUS_SWEET
    elif prefers_savory and item.sub_type == "savory":
        bonus *= BONUS_SAVORY

    # Energy boost for drowsy students
    if state.is_drowsy and item.energy_boost:
        bonus *= BONUS_ENERGY

    # High calorie bonus for active/high metabolism students
    is_active = profile.q5_activity_level in HIGH_ACTIVITY_LEVELS
    has_high_metabolism = profile.q3_metabolism in HIGH_METABOLISM_VALUES
    if (is_active or has_high_metabolism) and item.calories >= HIGH_CALORIE_THRESHOLD:
        bonus *= BONUS_HIGH_CALORIE

    # Category match bonus based on mood
    if state.mood == "healthy" and item.category == "healthy":
        bonus *= BONUS_CATEGORY_MATCH
    elif state.mood == "junk" and item.category in ("fried", "sweet"):
        bonus *= BONUS_CATEGORY_MATCH

    return bonus


def score_item(
    item: MenuItem,
    profile: StudentProfile,
    state: StudentDailyState,
) -> float:
    """Calculate total score for a menu item.

    Uses fuzzy matching to heavily weight items similar to student's favorite food.

    Args:
        item: The menu item to score
        profile: Student's permanent profile
        state: Student's daily state

    Returns:
        Total weighted score with bonuses applied
    """
    # Base scores
    preference_score, fuzzy_score = _score_preference(item, profile)
    affordability_score = _score_affordability(item, state)
    mood_score = _score_mood_health(item, state)

    # Can't buy if not affordable
    if affordability_score == 0:
        return 0.0

    # Weighted base score
    base_score = (
        WEIGHT_PREFERENCE * preference_score
        + WEIGHT_AFFORDABILITY * affordability_score
        + WEIGHT_MOOD_HEALTH * mood_score
    )

    # Apply bonuses
    bonus_multiplier = _calculate_bonuses(item, profile, state, fuzzy_score)

    return base_score * bonus_multiplier


