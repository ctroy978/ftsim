"""Console output reporting for the food truck simulation."""

import json
from pathlib import Path
from typing import Optional

from .results import DailyResult, AggregateResult


def print_daily_summary(result: DailyResult) -> None:
    """Print summary for a single day."""
    print(f"\n{'=' * 50}")
    print(f"Day {result.day} Summary")
    print(f"{'=' * 50}")
    print(f"Revenue: ${result.revenue:.2f}")
    print(f"Customers: {result.customers}/{result.total_students} ({result.customers/result.total_students*100:.1f}%)")
    print(f"School Lunch Price: ${result.school_lunch_price:.2f}")

    if result.items_sold:
        print("\nItems Sold:")
        for item_name, count in sorted(result.items_sold.items(), key=lambda x: -x[1]):
            print(f"  {item_name}: {count}")

    if result.stockouts:
        print("\nStockouts (sold out):")
        for item_name, count in result.stockouts.items():
            if count > 0:
                print(f"  {item_name}: sold out")

    if result.losses_by_reason:
        print("\nLost Sales:")
        for reason, count in sorted(result.losses_by_reason.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")


def print_aggregate_summary(result: AggregateResult) -> None:
    """Print aggregate summary for entire simulation."""
    print(f"\n{'#' * 60}")
    print(f"SIMULATION COMPLETE - {result.total_days} Days")
    print(f"{'#' * 60}")

    print("\n--- TOTALS ---")
    print(f"Total Revenue: ${result.total_revenue:.2f}")
    print(f"Total Customers: {result.total_customers}")
    print(f"Total Students Processed: {result.total_students_served}")

    print("\n--- AVERAGES ---")
    print(f"Daily Revenue: ${result.avg_daily_revenue:.2f}")
    print(f"Daily Customers: {result.avg_daily_customers:.1f}")
    print(f"Customer Rate: {result.customer_rate * 100:.1f}%")
    print(f"Items per Customer: {result.avg_items_per_customer:.2f}")

    if result.total_items_sold:
        print("\n--- ITEMS SOLD (Total) ---")
        for item_name, count in sorted(result.total_items_sold.items(), key=lambda x: -x[1]):
            print(f"  {item_name}: {count}")

    if result.total_stockouts:
        total_stockout_days = sum(result.total_stockouts.values())
        if total_stockout_days > 0:
            print("\n--- STOCKOUTS (Days Sold Out) ---")
            for item_name, days in sorted(result.total_stockouts.items(), key=lambda x: -x[1]):
                if days > 0:
                    print(f"  {item_name}: {days} days")

    if result.total_losses_by_reason:
        print("\n--- LOST SALES BY REASON ---")
        total_losses = sum(result.total_losses_by_reason.values())
        for reason, count in sorted(result.total_losses_by_reason.items(), key=lambda x: -x[1]):
            pct = count / total_losses * 100 if total_losses > 0 else 0
            print(f"  {reason}: {count} ({pct:.1f}%)")


def export_json(result: AggregateResult, output_path: str) -> None:
    """Export results to JSON file.

    Args:
        result: Aggregate simulation results
        output_path: Path to output JSON file
    """
    path = Path(output_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"\nResults exported to: {path}")
