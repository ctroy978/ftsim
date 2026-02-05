"""Main simulation engine for the food truck simulation."""

import random
from typing import List, Dict

from ..models.student import StudentProfile, StudentDailyState
from ..models.menu_item import MenuItem
from ..models.vendors import FoodTruck, SchoolLunch, FastFood
from ..output.results import (
    DailyResult,
    TruckDailyResult,
    TruckAggregateResult,
    CompetitionAggregateResult,
)
from .daily_state import generate_daily_states
from .decision import make_decision


class SimulationEngine:
    """Main simulation engine that runs the food truck simulation."""

    def __init__(
        self,
        students: List[StudentProfile],
        trucks: List[FoodTruck],
        num_days: int = 30,
        verbose: bool = False,
    ):
        """Initialize the simulation.

        Args:
            students: List of student profiles
            trucks: List of food trucks competing
            num_days: Number of days to simulate
            verbose: Whether to print daily summaries
        """
        self.students = students
        self.trucks = trucks
        self.school_lunch = SchoolLunch()
        self.fast_food = FastFood()
        self.num_days = num_days
        self.verbose = verbose

    def _run_day(self, day: int) -> DailyResult:
        """Run simulation for a single day.

        Args:
            day: Day number (1-indexed)

        Returns:
            DailyResult with day's outcomes
        """
        # Reset inventory for all trucks
        for truck in self.trucks:
            truck.reset_inventory()

        # Generate school lunch price
        self.school_lunch.generate_daily_price()

        # Generate daily states for all students
        daily_states = generate_daily_states(self.students)

        # Create lookup from student_id to profile
        profile_lookup = {p.student_id: p for p in self.students}

        # Shuffle order (simulates random arrival)
        random.shuffle(daily_states)

        # Track results per truck
        truck_revenue: Dict[str, float] = {truck.name: 0.0 for truck in self.trucks}
        truck_customers: Dict[str, int] = {truck.name: 0 for truck in self.trucks}
        truck_items_sold: Dict[str, Dict[str, int]] = {truck.name: {} for truck in self.trucks}
        truck_stockouts: Dict[str, Dict[str, int]] = {
            truck.name: {item.name: 0 for item in truck.menu} for truck in self.trucks
        }

        losses_by_reason: Dict[str, int] = {}
        student_state_dicts = []

        # Track inventory to detect when items sell out
        prev_inventory: Dict[str, Dict[str, int]] = {
            truck.name: {item.name: item.current_inventory for item in truck.menu}
            for truck in self.trucks
        }

        # Process each student
        for state in daily_states:
            profile = profile_lookup[state.student_id]

            # Make decision
            make_decision(profile, state, self.trucks, self.school_lunch)

            # Record results
            if state.purchased_items and state.purchased_from_truck:
                truck_name = state.purchased_from_truck
                truck_customers[truck_name] += 1
                truck_revenue[truck_name] += state.total_spent
                for item in state.purchased_items:
                    truck_items_sold[truck_name][item.name] = (
                        truck_items_sold[truck_name].get(item.name, 0) + 1
                    )

            if state.loss_reason:
                losses_by_reason[state.loss_reason] = (
                    losses_by_reason.get(state.loss_reason, 0) + 1
                )

            # Check for new stockouts per truck
            for truck in self.trucks:
                for item in truck.menu:
                    if (
                        prev_inventory[truck.name][item.name] > 0
                        and item.current_inventory == 0
                    ):
                        truck_stockouts[truck.name][item.name] = 1
                    prev_inventory[truck.name][item.name] = item.current_inventory

            # Store state for export
            student_state_dicts.append(state.to_dict())

        # Build truck results
        truck_results: Dict[str, TruckDailyResult] = {}
        for truck in self.trucks:
            truck_results[truck.name] = TruckDailyResult(
                truck_name=truck.name,
                revenue=truck_revenue[truck.name],
                customers=truck_customers[truck.name],
                items_sold=truck_items_sold[truck.name],
                stockouts=truck_stockouts[truck.name],
            )

        return DailyResult(
            day=day,
            truck_results=truck_results,
            losses_by_reason=losses_by_reason,
            total_students=len(self.students),
            school_lunch_price=self.school_lunch.price,
            student_states=student_state_dicts,
        )

    def run(self) -> CompetitionAggregateResult:
        """Run the full simulation.

        Returns:
            CompetitionAggregateResult with all simulation data
        """
        daily_results: List[DailyResult] = []

        for day in range(1, self.num_days + 1):
            result = self._run_day(day)
            daily_results.append(result)

            if self.verbose:
                from ..output.reporter import print_daily_summary
                print_daily_summary(result)

        # Aggregate results per truck
        truck_aggregate: Dict[str, TruckAggregateResult] = {}

        for truck in self.trucks:
            truck_name = truck.name
            total_revenue = sum(
                r.truck_results[truck_name].revenue for r in daily_results
            )
            total_customers = sum(
                r.truck_results[truck_name].customers for r in daily_results
            )

            # Aggregate items sold for this truck
            total_items_sold: Dict[str, int] = {}
            for result in daily_results:
                for item_name, count in result.truck_results[truck_name].items_sold.items():
                    total_items_sold[item_name] = total_items_sold.get(item_name, 0) + count

            # Aggregate stockouts for this truck
            total_stockouts: Dict[str, int] = {}
            for result in daily_results:
                for item_name, sold_out in result.truck_results[truck_name].stockouts.items():
                    total_stockouts[item_name] = total_stockouts.get(item_name, 0) + sold_out

            truck_aggregate[truck_name] = TruckAggregateResult(
                truck_name=truck_name,
                total_revenue=total_revenue,
                total_customers=total_customers,
                total_items_sold=total_items_sold,
                total_stockouts=total_stockouts,
                avg_daily_revenue=total_revenue / self.num_days,
                avg_daily_customers=total_customers / self.num_days,
            )

        # Aggregate losses across all trucks
        total_losses: Dict[str, int] = {}
        for result in daily_results:
            for reason, count in result.losses_by_reason.items():
                total_losses[reason] = total_losses.get(reason, 0) + count

        # Determine winner
        winner = max(truck_aggregate.keys(), key=lambda t: truck_aggregate[t].total_revenue)

        total_students_served = len(self.students) * self.num_days

        return CompetitionAggregateResult(
            total_days=self.num_days,
            truck_results=truck_aggregate,
            total_losses_by_reason=total_losses,
            total_students_served=total_students_served,
            winner=winner,
            daily_results=daily_results,
        )
