#!/usr/bin/env python3
"""Menu validation utility for the food truck simulation.

Validates that a menu YAML/JSON file is correctly formatted
and contains all required fields.
"""

import argparse
import sys
from pathlib import Path

from ftsim.data.loader import load_menu


def main():
    """Validate a menu file."""
    parser = argparse.ArgumentParser(
        description="Validate a food truck menu file (YAML or JSON)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_menu.py --menu sample_menu.yaml
  python validate_menu.py --menu my_menu.json
        """,
    )

    parser.add_argument(
        "--menu",
        required=True,
        help="Path to menu file (JSON or YAML)",
    )

    args = parser.parse_args()

    menu_path = Path(args.menu)
    if not menu_path.exists():
        print(f"Error: Menu file not found: {menu_path}", file=sys.stderr)
        return 1

    print(f"Validating: {menu_path}")
    print("-" * 50)

    try:
        menu_data = load_menu(str(menu_path))
    except ValueError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Success - print summary
    print(f"Company Name: {menu_data.name}")
    print(f"Total Items: {len(menu_data.items)}")
    print()

    # Categorize items
    food_items = [item for item in menu_data.items if item.item_type == "food"]
    drink_items = [item for item in menu_data.items if item.item_type == "drink"]

    print(f"Food Items ({len(food_items)}):")
    for item in food_items:
        print(f"  - {item.name}: ${item.price:.2f} | {item.category} | "
              f"health:{item.health_rating}/10 | {item.calories}cal | "
              f"inventory:{item.inventory_per_day}/day")

    print()
    print(f"Drink Items ({len(drink_items)}):")
    for item in drink_items:
        energy = " [ENERGY]" if item.energy_boost else ""
        print(f"  - {item.name}: ${item.price:.2f} | {item.category} | "
              f"health:{item.health_rating}/10 | {item.calories}cal | "
              f"inventory:{item.inventory_per_day}/day{energy}")

    print()
    print("-" * 50)
    print("VALID: Menu file is correctly formatted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
