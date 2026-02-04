#!/usr/bin/env python3
"""Food Truck Simulation - Main Entry Point.

Simulates a food truck competing against school lunch and fast food
at a high school lunch period over multiple days.
"""

import argparse
import random
import sys
from pathlib import Path

from ftsim.data.loader import load_students, load_menu
from ftsim.simulation.engine import SimulationEngine
from ftsim.output.reporter import print_aggregate_summary, export_json
from ftsim.config import DEFAULT_DAYS


def main():
    """Main entry point for the food truck simulation."""
    parser = argparse.ArgumentParser(
        description="Food Truck Simulation - Compete for high school lunch customers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --menu sample_menu.yaml
  python main.py --menu menu.json --days 30 --verbose
  python main.py --menu menu.yaml --seed 42 --export results.json
        """,
    )

    parser.add_argument(
        "--menu",
        required=True,
        help="Path to menu file (JSON or YAML)",
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
    menu_path = Path(args.menu)
    if not menu_path.exists():
        print(f"Error: Menu file not found: {menu_path}", file=sys.stderr)
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

    print("Loading menu...")
    menu_items = load_menu(str(menu_path))
    print(f"Loaded {len(menu_items)} menu items:")
    for item in menu_items:
        print(f"  - {item.name}: ${item.price:.2f} (inventory: {item.inventory_per_day}/day)")

    # Run simulation
    print(f"\nRunning simulation for {args.days} days...")
    engine = SimulationEngine(
        students=students,
        menu_items=menu_items,
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
