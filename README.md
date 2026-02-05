# Food Truck Simulation

A Python simulation where two food trucks compete head-to-head for high school lunch customers. Each truck has its own menu, and 1000 students choose between both trucks, school lunch, or fast food over N days. Track revenue, customers, stockouts, and see which truck wins.

## Running the Simulation

```bash
# Basic head-to-head run with two menu files
uv run main.py --menu1 sample_menu.yaml --menu2 sample_menu2.yaml

# Run for 30 days with daily output
uv run main.py --menu1 sample_menu.yaml --menu2 sample_menu2.yaml --days 30 --verbose

# Use a seed for reproducible results
uv run main.py --menu1 sample_menu.yaml --menu2 sample_menu2.yaml --seed 42

# Export results to JSON for analysis
uv run main.py --menu1 sample_menu.yaml --menu2 sample_menu2.yaml --export results.json

# Full example
uv run main.py --menu1 my_menu.yaml --menu2 competitor.yaml --days 30 --seed 42 --verbose --export results.json
```

### Command Line Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--menu1` | Yes | - | Path to first truck's menu file (JSON or YAML) |
| `--menu2` | Yes | - | Path to second truck's menu file (JSON or YAML) |
| `--days` | No | 30 | Number of days to simulate |
| `--seed` | No | Random | Random seed for reproducible results |
| `--verbose` | No | Off | Print daily summaries |
| `--export` | No | None | Export results to JSON file |
| `--data-dir` | No | `data` | Directory containing CSV data files |

## Validating Menu Files

Before running a simulation, you can validate that your menu file is correctly formatted using the validation utility:

```bash
# Validate a menu file
uv run validate_menu.py --menu my_menu.yaml
```

This will check that:
- The file is valid YAML/JSON
- A company `name` is provided
- All required fields are present for each item
- All field values are within valid ranges (e.g., health_rating 1-10)
- Categories and types are valid

On success, you'll see a summary of your menu:

```
Validating: my_menu.yaml
--------------------------------------------------
Company Name: Taco Express
Total Items: 8

Food Items (5):
  - Chicken Tacos: $7.50 | savory | health:6/10 | 450cal | inventory:60/day
  ...

Drink Items (3):
  - Horchata: $3.00 | milk | health:4/10 | 180cal | inventory:50/day
  ...

--------------------------------------------------
VALID: Menu file is correctly formatted.
```

On failure, you'll see a specific error message:

```
INVALID: Menu item 'Bad Item' has invalid health_rating 15. Must be between 1 and 10
```

## Creating Menu Files

Menu files define what your food truck sells. You can use either YAML or JSON format. **All fields are required** for each menu item.

### Menu File Structure

Each menu file must have:
- A `name` field with your company/truck name (displayed in results)
- An `items` array containing your menu items

### Required Fields

| Field | Type | Valid Values | Description |
|-------|------|--------------|-------------|
| `name` | string | Any text | Display name of the item. **Tip:** Use names similar to popular student favorites for higher sales (see Favorite Food Matching below) |
| `price` | number | > 0 | Price in dollars (e.g., 8.50) |
| `health_rating` | integer | 1-10 | Health score (1=unhealthy, 10=very healthy) |
| `type` | string | `"food"`, `"drink"` | Whether this is a food or drink item |
| `category` | string | See below | The item's category for preference matching |
| `sub_type` | string | `"sweet"`, `"savory"` | Flavor profile - affects student preference bonuses |
| `energy_boost` | boolean | `true`, `false` | Does this item provide energy? (coffee, energy drinks) |
| `inventory_per_day` | integer | > 0 | How many you can sell per day |
| `calories` | integer | >= 0 | Calorie count (items >= 600 appeal to active students) |

### Category Values

**For food items (`type: food`):**
| Category | Description | Example Items |
|----------|-------------|---------------|
| `healthy` | Nutritious, lighter options | Salads, grilled wraps, fruit cups, yogurt parfaits |
| `fried` | Deep-fried, indulgent foods | Fries, chicken tenders, onion rings, nachos |
| `sweet` | Desserts and pastries | Brownies, cookies, churros, ice cream |
| `savory` | Hearty main dishes | Chicken bowls, burritos, sandwiches, tacos |
| `snack` | Small sides and extras | Garlic knots, mozzarella sticks |

**For drink items (`type: drink`):**
| Category | Description | Example Items |
|----------|-------------|---------------|
| `energy` | Energy drinks | Red Bull, Monster, Rockstar |
| `soda` | Carbonated soft drinks | Coca-Cola, Pepsi, Dr Pepper, Sprite |
| `juice` | Fruit juices and smoothies | Orange juice, lemonade, fruit punch |
| `water` | Plain and sparkling water | Bottled water, sparkling water |
| `milk` | Dairy drinks | Regular milk, chocolate milk, strawberry milk |
| `coffee` | Coffee and tea drinks | Iced coffee, black coffee, sweet tea |

### YAML Example

```yaml
name: "Fusion Bites"

items:
  - name: "Teriyaki Chicken Bowl"
    price: 9.00
    health_rating: 7
    type: food
    category: savory
    sub_type: savory
    energy_boost: false
    inventory_per_day: 50
    calories: 650

  - name: "Veggie Burrito Bowl"
    price: 8.00
    health_rating: 8
    type: food
    category: healthy
    sub_type: savory
    energy_boost: false
    inventory_per_day: 40
    calories: 520

  - name: "Loaded Nachos"
    price: 7.50
    health_rating: 3
    type: food
    category: fried
    sub_type: savory
    energy_boost: false
    inventory_per_day: 60
    calories: 780

  - name: "Chocolate Brownie"
    price: 3.50
    health_rating: 2
    type: food
    category: sweet
    sub_type: sweet
    energy_boost: false
    inventory_per_day: 50
    calories: 380

  - name: "Red Bull Style Energy Drink"
    price: 3.50
    health_rating: 2
    type: drink
    category: energy
    sub_type: sweet
    energy_boost: true
    inventory_per_day: 80
    calories: 110

  - name: "Fresh Lemonade"
    price: 3.00
    health_rating: 5
    type: drink
    category: juice
    sub_type: sweet
    energy_boost: false
    inventory_per_day: 60
    calories: 150

  - name: "Bottled Water"
    price: 1.50
    health_rating: 10
    type: drink
    category: water
    sub_type: savory
    energy_boost: false
    inventory_per_day: 100
    calories: 0
```

### JSON Example

```json
{
  "name": "Fusion Bites",
  "items": [
    {
      "name": "Teriyaki Chicken Bowl",
      "price": 9.00,
      "health_rating": 7,
      "type": "food",
      "category": "savory",
      "sub_type": "savory",
      "energy_boost": false,
      "inventory_per_day": 50,
      "calories": 650
    },
    {
      "name": "Red Bull Style Energy Drink",
      "price": 3.50,
      "health_rating": 2,
      "type": "drink",
      "category": "energy",
      "sub_type": "sweet",
      "energy_boost": true,
      "inventory_per_day": 80,
      "calories": 110
    },
    {
      "name": "Bottled Water",
      "price": 1.50,
      "health_rating": 10,
      "type": "drink",
      "category": "water",
      "sub_type": "savory",
      "energy_boost": false,
      "inventory_per_day": 100,
      "calories": 0
    }
  ]
}
```

## Menu Design Tips

### Favorite Food Matching (Most Important!)

Each student has a favorite food from the survey data. The simulation uses **fuzzy matching** to compare your menu item names against student favorites. Items with names similar to popular favorites get massive bonuses:

- **High match (85%+ similarity):** +100% bonus
- **Medium match (70%+ similarity):** +50% bonus

**Popular student favorites from the data:**
- Fruit & Yogurt Parfait (154 students)
- Turkey & Avocado Sandwich (87 students)
- Double Bacon Cheeseburger (62 students)
- Vegetable Stir-Fry with Rice (58 students)
- Veggie Burrito Bowl (53 students)
- Carne Asada Fries (49 students)
- Teriyaki Chicken Bowl (44 students)
- Churro with Cinnamon Sugar (41 students)
- Chicken Tenders + Fries (41 students)
- Grilled Chicken Wrap (34 students)
- Cinnamon Roll (34 students)

**Tip:** Name your items similarly to these favorites! "Teriyaki Chicken Bowl" will strongly match students who listed that as their favorite.

### Category Matching

Categories help match items to student preferences based on their mood:
- **Healthy mood students** get a +35% bonus for `category: healthy` items
- **Junk mood students** get a +35% bonus for `category: fried` or `category: sweet` items

### Pricing Strategy
- Students have varying budgets ($5-$14 depending on income level)
- School lunch costs $0-$2, so you're competing on value/preference
- Most students have $7-$10 to spend

### Health Ratings
- Health-conscious students (about 50%) prefer items with ratings 7+
- Students in "junk food" mood prefer items with ratings 3 or below
- Balance your menu to capture both segments

### Energy Boost Items
- 30% of students are drowsy each day
- Drowsy students get a +30% score bonus for energy items
- Energy drinks and coffee are popular with this group

### Inventory Management
- High inventory = fewer stockouts but ties up variety
- Low inventory = stockouts lose sales to school lunch
- Watch the stockout report to adjust quantities

### Sweet vs Savory
- Students who want sweets get a +25% bonus for `sub_type: sweet` items
- Students who prefer savory get a +20% bonus for `sub_type: savory` items
- Mark desserts and sweet drinks with `sub_type: sweet`

### High Calorie Items
- Active students and those with fast metabolism prefer 600+ calorie items
- They get a +20% score bonus for high-calorie options

## Understanding the Output

### Daily Summary (with --verbose)
```
============================================================
Day 1 Summary
============================================================
School Lunch Price: $0.38

--- Fusion Bites ---
Revenue: $2961.00
Customers: 310 (31.0%)
Items Sold:
  Red Bull style energy drink: 80
  Loaded Nachos: 60
  ...
Stockouts: Teriyaki Chicken Bowl, Veggie Burrito Bowl, ...

--- Pizza Paradise ---
Revenue: $2226.50
Customers: 365 (36.5%)
Items Sold:
  Fountain Soda: 132
  Pepperoni Pizza Slice: 100
  ...
Stockouts: Pepperoni Pizza Slice, Veggie Pizza Slice, ...

--- Combined ---
Total Revenue: $5187.50
Total Customers: 675/1000

Lost Sales:
  school_lunch: 278    # Chose school lunch over both trucks
  fastfood: 47         # Students with cars who chose fast food
```

### Aggregate Summary
```
############################################################
SIMULATION COMPLETE - 30 Days
############################################################

************************************************************
  WINNER: Fusion Bites
  Total Revenue: $88,770.00
************************************************************

============================================================
HEAD-TO-HEAD COMPARISON
============================================================
Metric                      Fusion Bites Pizza Paradise
------------------------------------------------------------
Total Revenue            $     88,770.00$     66,420.00
Total Customers                    9,300         10,950
Avg Daily Revenue        $      2,959.00$      2,214.00
Avg Daily Customers                310.0          365.0

============================================================
Fusion Bites - DETAILED RESULTS
============================================================
Total Revenue: $88,770.00
Total Customers: 9,300
...

============================================================
COMBINED STATISTICS
============================================================
Total Students Processed: 30,000
Combined Customer Rate: 67.5%

Lost Sales by Reason:
  school_lunch: 8,340 (85.1%)  # Chose school lunch
  fastfood: 1,410 (14.9%)      # Lost to drive-through
```

### Loss Reasons
| Reason | Meaning |
|--------|---------|
| `school_lunch` | Student chose school lunch over your menu |
| `price` | Student couldn't afford any items |
| `stockout` | All appealing items were sold out |
| `fastfood` | Student with car chose fast food (junk mood) |

## JSON Export Format

The `--export` option creates a JSON file with complete simulation data:

```json
{
  "summary": {
    "total_days": 30,
    "total_revenue": 155190.00,
    "total_customers": 20250,
    "total_losses_by_reason": {"school_lunch": 8340, "fastfood": 1410},
    "total_students_served": 30000,
    "winner": "Fusion Bites"
  },
  "truck_results": {
    "Fusion Bites": {
      "truck_name": "Fusion Bites",
      "total_revenue": 88770.00,
      "total_customers": 9300,
      "total_items_sold": {"Teriyaki Chicken Bowl": 1500, ...},
      "total_stockouts": {"Teriyaki Chicken Bowl": 30, ...},
      "avg_daily_revenue": 2959.00,
      "avg_daily_customers": 310.0
    },
    "Pizza Paradise": {
      "truck_name": "Pizza Paradise",
      "total_revenue": 66420.00,
      "total_customers": 10950,
      "total_items_sold": {"Pepperoni Pizza Slice": 3000, ...},
      "total_stockouts": {"Pepperoni Pizza Slice": 30, ...},
      "avg_daily_revenue": 2214.00,
      "avg_daily_customers": 365.0
    }
  },
  "daily_results": [
    {
      "day": 1,
      "truck_results": {
        "Fusion Bites": {"revenue": 2961.00, "customers": 310, ...},
        "Pizza Paradise": {"revenue": 2226.50, "customers": 365, ...}
      },
      "total_revenue": 5187.50,
      "total_customers": 675,
      "losses_by_reason": {...},
      "student_states": [...]
    }
  ]
}
```

This format is designed for integration with Pygame or other visualization tools.
