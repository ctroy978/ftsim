"""Main simulation engine for the food truck simulation."""

import random
from typing import List, Dict

from ..models.student import StudentProfile, StudentDailyState
from ..models.menu_item import MenuItem
from ..models.vendors import FoodTruck, SchoolLunch, FastFood
from ..output.results import DailyResult, AggregateResult
from .daily_state import generate_daily_states
from .decision import make_decision


class SimulationEngine:
    """Main simulation engine that runs the food truck simulation."""

    def __init__(
        self,
        students: List[StudentProfile],
        menu_items: List[MenuItem],
        num_days: int = 30,
        verbose: bool = False,
    ):
        """Initialize the simulation.

        Args:
            students: List of student profiles
            menu_items: List of menu items for the food truck
            num_days: Number of days to simulate
            verbose: Whether to print daily summaries
        """
        self.students = students
        self.truck = FoodTruck(menu=menu_items)
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
        # Reset inventory
        self.truck.reset_inventory()

        # Generate school lunch price
        self.school_lunch.generate_daily_price()

        # Generate daily states for all students
        daily_states = generate_daily_states(self.students)

        # Create lookup from student_id to profile
        profile_lookup = {p.student_id: p for p in self.students}

        # Shuffle order (simulates random arrival)
        random.shuffle(daily_states)

        # Track results
        revenue = 0.0
        customers = 0
        items_sold: Dict[str, int] = {}
        stockouts: Dict[str, int] = {item.name: 0 for item in self.truck.menu}
        losses_by_reason: Dict[str, int] = {}
        student_state_dicts = []

        # Track inventory to detect when items sell out
        prev_inventory = {item.name: item.current_inventory for item in self.truck.menu}

        # Process each student
        for state in daily_states:
            profile = profile_lookup[state.student_id]

            # Make decision
            make_decision(profile, state, self.truck, self.school_lunch)

            # Record results
            if state.purchased_items:
                customers += 1
                revenue += state.total_spent
                for item in state.purchased_items:
                    items_sold[item.name] = items_sold.get(item.name, 0) + 1

            if state.loss_reason:
                losses_by_reason[state.loss_reason] = (
                    losses_by_reason.get(state.loss_reason, 0) + 1
                )

            # Check for new stockouts
            for item in self.truck.menu:
                if prev_inventory[item.name] > 0 and item.current_inventory == 0:
                    stockouts[item.name] = 1
                prev_inventory[item.name] = item.current_inventory

            # Store state for export
            student_state_dicts.append(state.to_dict())

        return DailyResult(
            day=day,
            revenue=revenue,
            customers=customers,
            items_sold=items_sold,
            stockouts=stockouts,
            losses_by_reason=losses_by_reason,
            total_students=len(self.students),
            school_lunch_price=self.school_lunch.price,
            student_states=student_state_dicts,
        )

    def run(self) -> AggregateResult:
        """Run the full simulation.

        Returns:
            AggregateResult with all simulation data
        """
        daily_results: List[DailyResult] = []

        for day in range(1, self.num_days + 1):
            result = self._run_day(day)
            daily_results.append(result)

            if self.verbose:
                from ..output.reporter import print_daily_summary
                print_daily_summary(result)

        # Aggregate results
        total_revenue = sum(r.revenue for r in daily_results)
        total_customers = sum(r.customers for r in daily_results)

        # Aggregate items sold
        total_items_sold: Dict[str, int] = {}
        for result in daily_results:
            for item_name, count in result.items_sold.items():
                total_items_sold[item_name] = total_items_sold.get(item_name, 0) + count

        # Aggregate stockouts (count days each item sold out)
        total_stockouts: Dict[str, int] = {}
        for result in daily_results:
            for item_name, sold_out in result.stockouts.items():
                total_stockouts[item_name] = total_stockouts.get(item_name, 0) + sold_out

        # Aggregate losses
        total_losses: Dict[str, int] = {}
        for result in daily_results:
            for reason, count in result.losses_by_reason.items():
                total_losses[reason] = total_losses.get(reason, 0) + count

        # Calculate averages
        total_students_served = len(self.students) * self.num_days
        avg_daily_revenue = total_revenue / self.num_days
        avg_daily_customers = total_customers / self.num_days

        total_items = sum(total_items_sold.values())
        avg_items_per_customer = total_items / total_customers if total_customers > 0 else 0

        customer_rate = total_customers / total_students_served if total_students_served > 0 else 0

        return AggregateResult(
            total_days=self.num_days,
            total_revenue=total_revenue,
            total_customers=total_customers,
            total_items_sold=total_items_sold,
            total_stockouts=total_stockouts,
            total_losses_by_reason=total_losses,
            total_students_served=total_students_served,
            avg_daily_revenue=avg_daily_revenue,
            avg_daily_customers=avg_daily_customers,
            avg_items_per_customer=avg_items_per_customer,
            customer_rate=customer_rate,
            daily_results=daily_results,
        )
