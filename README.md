# Food Truck Simulation

A Python simulation where students design a food truck menu to compete against school lunch and fast food at a high school lunch period. Simulates 1000 students over N days, tracking sales, stockouts, and competitor losses.

## Running the Simulation

```bash
# Basic run with a menu file
uv run main.py --menu sample_menu.yaml

# Run for 30 days with daily output
uv run main.py --menu sample_menu.yaml --days 30 --verbose

# Use a seed for reproducible results
uv run main.py --menu sample_menu.yaml --seed 42

# Export results to JSON for analysis or Pygame
uv run main.py --menu sample_menu.yaml --export results.json

# Full example
uv run main.py --menu my_menu.yaml --days 30 --seed 42 --verbose --export results.json
```

### Command Line Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--menu` | Yes | - | Path to your menu file (JSON or YAML) |
| `--days` | No | 30 | Number of days to simulate |
| `--seed` | No | Random | Random seed for reproducible results |
| `--verbose` | No | Off | Print daily summaries |
| `--export` | No | None | Export results to JSON file |
| `--data-dir` | No | `data` | Directory containing CSV data files |

## Creating Menu Files

Menu files define what your food truck sells. You can use either YAML or JSON format. **All fields are required** for each menu item.

### Menu File Structure

Each menu file must have an `items` array containing your menu items.

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
Day 1 Summary
==================================================
Revenue: $2955.00
Customers: 310/1000 (31.0%)
School Lunch Price: $0.38

Items Sold:
  Red Bull style energy drink: 80
  Loaded Nachos: 60
  ...

Stockouts (sold out):
  Red Bull style energy drink: sold out
  ...

Lost Sales:
  school_lunch: 643    # Chose school lunch over your menu
  fastfood: 47         # Students with cars who chose fast food
```

### Aggregate Summary
```
SIMULATION COMPLETE - 30 Days
--- TOTALS ---
Total Revenue: $88,770.00
Total Customers: 9,300

--- AVERAGES ---
Daily Revenue: $2,959.00
Customer Rate: 31.0%
Items per Customer: 1.81

--- LOST SALES BY REASON ---
  school_lunch: 19,248 (93.0%)  # Chose school lunch
  fastfood: 1,452 (7.0%)        # Lost to drive-through
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
    "total_revenue": 88770.00,
    "total_customers": 9300,
    "total_items_sold": {"Item Name": 500, ...},
    "total_stockouts": {"Item Name": 15, ...},
    "total_losses_by_reason": {"preference": 19248, ...}
  },
  "averages": {
    "daily_revenue": 2959.00,
    "daily_customers": 310.0,
    "items_per_customer": 1.81,
    "customer_rate_percent": 31.0
  },
  "daily_results": [
    {
      "day": 1,
      "revenue": 2955.00,
      "customers": 310,
      "items_sold": {...},
      "stockouts": {...},
      "losses_by_reason": {...},
      "student_states": [...]
    }
  ]
}
```

This format is designed for integration with Pygame or other visualization tools.
