#!/usr/bin/env python3
"""Food Truck Simulation - Main Entry Point.

Simulates two food trucks competing head-to-head against each other
(and school lunch/fast food) at a high school lunch period.
"""

import argparse
import random
import sys
from pathlib import Path

from ftsim.data.loader import load_students, load_menu
from ftsim.models.vendors import FoodTruck
from ftsim.simulation.engine import SimulationEngine
from ftsim.output.reporter import print_aggregate_summary, export_json
from ftsim.config import DEFAULT_DAYS


def main():
    """Main entry point for the food truck simulation."""
    parser = argparse.ArgumentParser(
        description="Food Truck Simulation - Two trucks compete head-to-head for high school lunch customers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --menu1 tacos.yaml --menu2 pizza.yaml
  python main.py --menu1 menu1.yaml --menu2 menu2.yaml --days 30 --verbose
  python main.py --menu1 menu1.yaml --menu2 menu2.yaml --seed 42 --export results.json
        """,
    )

    parser.add_argument(
        "--menu1",
        required=True,
        help="Path to first truck's menu file (JSON or YAML)",
    )
    parser.add_argument(
        "--menu2",
        required=True,
        help="Path to second truck's menu file (JSON or YAML)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Number of days to simulate (default: {DEFAULT_DAYS})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print daily summaries",
    )
    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="Export results to JSON file",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory containing CSV data files (default: data)",
    )

    args = parser.parse_args()

    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")

    # Validate paths
    menu1_path = Path(args.menu1)
    menu2_path = Path(args.menu2)

    if not menu1_path.exists():
        print(f"Error: Menu file not found: {menu1_path}", file=sys.stderr)
        sys.exit(1)

    if not menu2_path.exists():
        print(f"Error: Menu file not found: {menu2_path}", file=sys.stderr)
        sys.exit(1)

    data_dir = Path(args.data_dir)
    food_csv = data_dir / "student_food.csv"
    drink_csv = data_dir / "drink_preferences_survey_500.csv"

    if not food_csv.exists():
        print(f"Error: Student food data not found: {food_csv}", file=sys.stderr)
        sys.exit(1)

    if not drink_csv.exists():
        print(f"Error: Drink preferences data not found: {drink_csv}", file=sys.stderr)
        sys.exit(1)

    # Load data
    print("Loading student data...")
    students = load_students(str(food_csv), str(drink_csv), args.seed)
    print(f"Loaded {len(students)} students")

    # Load menus and create trucks
    print("\nLoading menus...")

    menu1_data = load_menu(str(menu1_path))
    truck1 = FoodTruck(name=menu1_data.name, menu=menu1_data.items)
    print(f"\nTruck 1: {truck1.name}")
    print(f"  {len(menu1_data.items)} menu items:")
    for item in menu1_data.items:
        print(f"    - {item.name}: ${item.price:.2f} (inventory: {item.inventory_per_day}/day)")

    menu2_data = load_menu(str(menu2_path))
    truck2 = FoodTruck(name=menu2_data.name, menu=menu2_data.items)
    print(f"\nTruck 2: {truck2.name}")
    print(f"  {len(menu2_data.items)} menu items:")
    for item in menu2_data.items:
        print(f"    - {item.name}: ${item.price:.2f} (inventory: {item.inventory_per_day}/day)")

    # Run simulation
    print(f"\nRunning head-to-head simulation for {args.days} days...")
    engine = SimulationEngine(
        students=students,
        trucks=[truck1, truck2],
        num_days=args.days,
        verbose=args.verbose,
    )

    results = engine.run()

    # Print summary
    print_aggregate_summary(results)

    # Export if requested
    if args.export:
        export_json(results, args.export)

    return 0


if __name__ == "__main__":
    sys.exit(main())
