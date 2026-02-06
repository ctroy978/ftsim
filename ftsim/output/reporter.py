"""Console output reporting for the food truck simulation."""

import csv
import json
from pathlib import Path
from typing import List

from .results import DailyResult, CompetitionAggregateResult


def print_daily_summary(result: DailyResult) -> None:
    """Print summary for a single day."""
    print(f"\n{'=' * 60}")
    print(f"Day {result.day} Summary")
    print(f"{'=' * 60}")
    print(f"School Lunch Price: ${result.school_lunch_price:.2f}")

    # Print per-truck results
    for truck_name, truck_result in result.truck_results.items():
        print(f"\n--- {truck_name} ---")
        print(f"Revenue: ${truck_result.revenue:.2f}")
        customer_pct = (
            truck_result.customers / result.total_students * 100
            if result.total_students > 0
            else 0
        )
        print(f"Customers: {truck_result.customers} ({customer_pct:.1f}%)")

        if truck_result.items_sold:
            print("Items Sold:")
            for item_name, count in sorted(
                truck_result.items_sold.items(), key=lambda x: -x[1]
            ):
                print(f"  {item_name}: {count}")

        stockout_items = [
            item_name
            for item_name, count in truck_result.stockouts.items()
            if count > 0
        ]
        if stockout_items:
            print("Stockouts: " + ", ".join(stockout_items))

    # Print combined stats
    print(f"\n--- Combined ---")
    print(f"Total Revenue: ${result.revenue:.2f}")
    print(f"Total Customers: {result.customers}/{result.total_students}")

    if result.losses_by_reason:
        print("\nLost Sales:")
        for reason, count in sorted(result.losses_by_reason.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")


def print_aggregate_summary(result: CompetitionAggregateResult) -> None:
    """Print aggregate summary for entire simulation."""
    print(f"\n{'#' * 60}")
    print(f"SIMULATION COMPLETE - {result.total_days} Days")
    print(f"{'#' * 60}")

    # Print winner banner
    winner_result = result.truck_results[result.winner]
    print(f"\n{'*' * 60}")
    print(f"  WINNER: {result.winner}")
    print(f"  Total Revenue: ${winner_result.total_revenue:.2f}")
    print(f"{'*' * 60}")

    # Print head-to-head comparison
    truck_names = list(result.truck_results.keys())
    print("\n" + "=" * 60)
    print("HEAD-TO-HEAD COMPARISON")
    print("=" * 60)

    # Header row
    header = f"{'Metric':<25}"
    for name in truck_names:
        header += f"{name:>15}"
    print(header)
    print("-" * 60)

    # Revenue row
    row = f"{'Total Revenue':<25}"
    for name in truck_names:
        row += f"${result.truck_results[name].total_revenue:>14,.2f}"
    print(row)

    # Customers row
    row = f"{'Total Customers':<25}"
    for name in truck_names:
        row += f"{result.truck_results[name].total_customers:>15,}"
    print(row)

    # Daily revenue row
    row = f"{'Avg Daily Revenue':<25}"
    for name in truck_names:
        row += f"${result.truck_results[name].avg_daily_revenue:>14,.2f}"
    print(row)

    # Daily customers row
    row = f"{'Avg Daily Customers':<25}"
    for name in truck_names:
        row += f"{result.truck_results[name].avg_daily_customers:>15,.1f}"
    print(row)

    # Print per-truck details
    for truck_name, truck_result in result.truck_results.items():
        print(f"\n{'=' * 60}")
        print(f"{truck_name} - DETAILED RESULTS")
        print(f"{'=' * 60}")

        print(f"\nTotal Revenue: ${truck_result.total_revenue:.2f}")
        print(f"Total Customers: {truck_result.total_customers}")
        print(f"Avg Daily Revenue: ${truck_result.avg_daily_revenue:.2f}")
        print(f"Avg Daily Customers: {truck_result.avg_daily_customers:.1f}")

        if truck_result.total_items_sold:
            print("\nItems Sold (Total):")
            for item_name, count in sorted(
                truck_result.total_items_sold.items(), key=lambda x: -x[1]
            ):
                print(f"  {item_name}: {count}")

        if truck_result.total_stockouts:
            total_stockout_days = sum(truck_result.total_stockouts.values())
            if total_stockout_days > 0:
                print("\nStockouts (Days Sold Out):")
                for item_name, days in sorted(
                    truck_result.total_stockouts.items(), key=lambda x: -x[1]
                ):
                    if days > 0:
                        print(f"  {item_name}: {days} days")

    # Print combined stats
    print(f"\n{'=' * 60}")
    print("COMBINED STATISTICS")
    print(f"{'=' * 60}")
    print(f"Total Students Processed: {result.total_students_served}")
    customer_rate = (
        result.total_customers / result.total_students_served * 100
        if result.total_students_served > 0
        else 0
    )
    print(f"Combined Customer Rate: {customer_rate:.1f}%")

    if result.total_losses_by_reason:
        print("\nLost Sales by Reason:")
        total_losses = sum(result.total_losses_by_reason.values())
        for reason, count in sorted(
            result.total_losses_by_reason.items(), key=lambda x: -x[1]
        ):
            pct = count / total_losses * 100 if total_losses > 0 else 0
            print(f"  {reason}: {count} ({pct:.1f}%)")


def export_csv(
    result: CompetitionAggregateResult,
    output_dir: str,
    truck_order: List[str],
) -> None:
    """Export results to CSV files, one set per truck.

    Creates 4 files:
    - menu1.csv / menu2.csv: Daily aggregate data per truck
    - menu1_students.csv / menu2_students.csv: Per-student purchase data per truck

    Args:
        result: Competition aggregate simulation results
        output_dir: Directory to write CSV files
        truck_order: List of truck names in order [menu1_truck, menu2_truck]
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Process each truck in order (menu1, menu2)
    menu_prefixes = ["menu1", "menu2"]
    for i, truck_name in enumerate(truck_order):
        menu_prefix = menu_prefixes[i]
        _write_daily_csv(result, output_path, truck_name, menu_prefix)
        _write_student_csv(result, output_path, truck_name, menu_prefix)

    print(f"\nResults exported to: {output_path}/")
    print(f"  - menu1.csv, menu1_students.csv ({truck_order[0]})")
    print(f"  - menu2.csv, menu2_students.csv ({truck_order[1]})")


def _write_daily_csv(
    result: CompetitionAggregateResult,
    output_path: Path,
    truck_name: str,
    menu_prefix: str,
) -> None:
    """Write daily aggregate CSV for a single truck."""
    csv_path = output_path / f"{menu_prefix}.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["day", "revenue", "customers", "items_sold", "stockouts"])

        for daily_result in result.daily_results:
            truck_result = daily_result.truck_results[truck_name]

            # JSON-encode items_sold dict
            items_sold_json = json.dumps(truck_result.items_sold)

            # Comma-separated list of stocked-out items
            stockout_items = [
                item for item, count in truck_result.stockouts.items() if count > 0
            ]
            stockouts_str = ",".join(stockout_items)

            writer.writerow([
                daily_result.day,
                round(truck_result.revenue, 2),
                truck_result.customers,
                items_sold_json,
                stockouts_str,
            ])


def _write_student_csv(
    result: CompetitionAggregateResult,
    output_path: Path,
    truck_name: str,
    menu_prefix: str,
) -> None:
    """Write per-student purchase CSV for a single truck."""
    csv_path = output_path / f"{menu_prefix}_students.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["day", "student_id", "purchased_items", "total_spent"])

        for daily_result in result.daily_results:
            for student_state in daily_result.student_states:
                # Only include students who purchased from this truck
                if student_state.get("purchased_from_truck") != truck_name:
                    continue

                purchased_items = ",".join(student_state.get("purchased_items", []))
                writer.writerow([
                    daily_result.day,
                    student_state.get("student_id"),
                    purchased_items,
                    round(student_state.get("total_spent", 0), 2),
                ])
