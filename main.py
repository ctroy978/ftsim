#!/usr/bin/env python3
"""Food Truck Simulation - Main Entry Point.

Simulates 2-4 food trucks competing head-to-head against each other
(and school lunch/fast food) at a high school lunch period.
"""

import argparse
import random
import sys
from pathlib import Path

from ftsim.data.loader import load_students, load_menu
from ftsim.models.vendors import FoodTruck
from ftsim.simulation.engine import SimulationEngine
from ftsim.output.reporter import print_aggregate_summary, export_csv
from ftsim.config import DEFAULT_DAYS


def main():
    """Main entry point for the food truck simulation."""
    parser = argparse.ArgumentParser(
        description="Food Truck Simulation - 2-4 trucks compete head-to-head for high school lunch customers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --menu1 tacos.yaml --menu2 pizza.yaml
  python main.py --menu1 menu1.yaml --menu2 menu2.yaml --menu3 menu3.yaml --days 30 --verbose
  python main.py --menu1 m1.yaml --menu2 m2.yaml --menu3 m3.yaml --menu4 m4.yaml --seed 42 --export results/
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
        "--menu3",
        default=None,
        help="Path to third truck's menu file (optional)",
    )
    parser.add_argument(
        "--menu4",
        default=None,
        help="Path to fourth truck's menu file (optional)",
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
        help="Export results to CSV files in the specified directory (creates menu1-menu4 .csv and _students.csv files)",
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

    # Collect menu paths in order, skipping those not provided
    menu_args = [args.menu1, args.menu2, args.menu3, args.menu4]
    menu_paths = []
    for i, menu_arg in enumerate(menu_args, start=1):
        if menu_arg is None:
            # menu3/menu4 not provided — stop here
            continue
        path = Path(menu_arg)
        if not path.exists():
            print(f"Error: Menu file not found: {path}", file=sys.stderr)
            sys.exit(1)
        menu_paths.append((i, path))

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
    trucks = []
    for truck_num, menu_path in menu_paths:
        menu_data = load_menu(str(menu_path))
        truck = FoodTruck(name=menu_data.name, menu=menu_data.items)
        trucks.append(truck)
        print(f"\nTruck {truck_num}: {truck.name}")
        print(f"  {len(menu_data.items)} menu items:")
        for item in menu_data.items:
            print(f"    - {item.name}: ${item.price:.2f} (inventory: {item.inventory_per_day}/day)")

    # Run simulation
    print(f"\nRunning head-to-head simulation for {args.days} days with {len(trucks)} trucks...")
    engine = SimulationEngine(
        students=students,
        trucks=trucks,
        num_days=args.days,
        verbose=args.verbose,
    )

    results = engine.run()

    # Print summary
    print_aggregate_summary(results)

    # Export if requested
    if args.export:
        truck_order = [truck.name for truck in trucks]
        export_csv(results, args.export, truck_order=truck_order)

    return 0


if __name__ == "__main__":
    sys.exit(main())
