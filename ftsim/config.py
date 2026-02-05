"""Configuration constants and mappings for the food truck simulation."""

# Simulation parameters
DROWSINESS_CHANCE = 0.30
HAS_CAR_PERCENTAGE = 0.20
MONEY_VARIANCE = 0.20  # Gaussian ±20% from base

# Scoring weights (must sum to 1.0)
WEIGHT_PREFERENCE = 0.50
WEIGHT_AFFORDABILITY = 0.30
WEIGHT_MOOD_HEALTH = 0.20

# Multiplicative bonuses
BONUS_FUZZY_MATCH_HIGH = 2.00  # +100% for high-confidence fuzzy match (>=85%)
BONUS_FUZZY_MATCH_MEDIUM = 1.50  # +50% for medium-confidence fuzzy match (>=70%)
BONUS_SWEET = 1.25  # +25% for sweet item when student wants sweet
BONUS_SAVORY = 1.20  # +20% for savory item when student prefers savory
BONUS_ENERGY = 1.30  # +30% for energy boost when drowsy
BONUS_HIGH_CALORIE = 1.20  # +20% for high calories (>=600) for active students
BONUS_CATEGORY_MATCH = 1.35  # +35% when item category matches student preferences

# Penalty for incomplete meal (can afford food but not drink)
PENALTY_NO_DRINK = 0.85  # 15% penalty when student can't afford food + drink combo

# Fuzzy match thresholds
FUZZY_THRESHOLD_HIGH = 85  # High confidence match
FUZZY_THRESHOLD_MEDIUM = 70  # Medium confidence match

# High calorie threshold
HIGH_CALORIE_THRESHOLD = 600

# Fast food chance when student has car and junk mood
FAST_FOOD_CHANCE = 0.50

# School lunch price range
SCHOOL_LUNCH_MIN_PRICE = 0.0
SCHOOL_LUNCH_MAX_PRICE = 2.0
SCHOOL_LUNCH_HEALTH_RATING = 6  # Moderate health rating

# Fast food price multiplier over truck prices
FAST_FOOD_PRICE_MULTIPLIER_MIN = 1.20
FAST_FOOD_PRICE_MULTIPLIER_MAX = 1.50

# Q4_MoneyForLunch + IncomeLevel → Base Money mapping
# Key: (Q4_MoneyForLunch, IncomeLevel) → base_money
MONEY_MAPPING = {
    ("Less than $7", "Low"): 5.00,
    ("Less than $7", "Medium"): 6.00,
    ("Less than $7", "High"): 6.50,
    ("$7-$10", "Low"): 7.50,
    ("$7-$10", "Medium"): 8.50,
    ("$7-$10", "High"): 9.50,
    ("More than $10", "Low"): 10.50,
    ("More than $10", "Medium"): 12.00,
    ("More than $10", "High"): 14.00,
}

# Q6_HealthyImportance → Healthy Mood Probability
HEALTHY_MOOD_PROBABILITY = {
    "Very important - I always try to choose nutritious options": 0.75,
    "Somewhat important - I try to balance healthy and tasty": 0.50,
    "Not really important - I just eat what tastes good": 0.25,
}

# Q7_WantsSweet → Sweet preference
# True if student wants sweet items
SWEET_PREFERENCE_VALUES = {
    "Yes, I often crave something sweet": True,
    "Sometimes": True,  # Treat as partial preference
    "Rarely": False,
    "No, I prefer savory": False,
}

# Q1_SpendOnDrink → Drink spend willingness (multiplier)
DRINK_SPEND_MAPPING = {
    "Less than $2": 1.5,
    "$2-$3": 2.5,
    "$3-$5": 4.0,
    "More than $5": 6.0,
}

# Q5_ActivityLevel values for high activity check
HIGH_ACTIVITY_LEVELS = {
    "Very active (exercise daily)",
    "Active (exercise 3-4 times a week)",
}

# Q3_Metabolism values for high metabolism check
HIGH_METABOLISM_VALUES = {
    "Fast - I can eat a lot without gaining weight",
}

# Q2_HealthGoal modifier for healthy mood probability
HEALTH_GOAL_MODIFIER = {
    "Lose weight": 0.10,  # More likely healthy mood
    "Maintain weight": 0.0,
    "Gain weight/muscle": -0.05,  # Slightly less health-focused
    "Not focused on weight": 0.0,
}

# Loss reasons
LOSS_REASON_SCHOOL_LUNCH = "school_lunch"
LOSS_REASON_PRICE = "price"
LOSS_REASON_STOCKOUT = "stockout"
LOSS_REASON_FASTFOOD = "fastfood"

# Item types
ITEM_TYPE_FOOD = "food"
ITEM_TYPE_DRINK = "drink"

# Food categories (for category field)
FOOD_CATEGORIES = {
    "healthy",      # Salads, fruit, yogurt, grilled items
    "fried",        # Fried foods, burgers, fries
    "sweet",        # Desserts, pastries, ice cream
    "savory",       # Main dishes, wraps, bowls
    "snack",        # Small items, sides
}

# Drink categories (for category field)
DRINK_CATEGORIES = {
    "energy",       # Energy drinks (Red Bull, Monster, Rockstar)
    "soda",         # Carbonated soft drinks
    "juice",        # Fruit juices, smoothies
    "water",        # Plain and sparkling water
    "milk",         # Regular, chocolate, strawberry milk
    "coffee",       # Coffee and tea drinks
}

# Valid sub_types
VALID_SUB_TYPES = {"sweet", "savory"}

# Default values
DEFAULT_DAYS = 30
DEFAULT_STUDENTS = 1000
