"""Daily state generation for students."""

import random
from typing import List

from ..models.student import StudentProfile, StudentDailyState
from ..config import (
    MONEY_MAPPING,
    HEALTHY_MOOD_PROBABILITY,
    HEALTH_GOAL_MODIFIER,
    DROWSINESS_CHANCE,
    MONEY_VARIANCE,
)


def _get_base_money(profile: StudentProfile) -> float:
    """Get base money for student based on Q4 and income level."""
    key = (profile.q4_money_for_lunch, profile.income_level)
    return MONEY_MAPPING.get(key, 8.50)  # Default to medium


def _get_healthy_mood_probability(profile: StudentProfile) -> float:
    """Get probability of healthy mood based on Q6 and Q2."""
    base_prob = HEALTHY_MOOD_PROBABILITY.get(
        profile.q6_healthy_importance, 0.50
    )
    modifier = HEALTH_GOAL_MODIFIER.get(profile.q2_health_goal, 0.0)
    return max(0.0, min(1.0, base_prob + modifier))


def generate_daily_state(profile: StudentProfile) -> StudentDailyState:
    """Generate randomized daily state for a single student.

    Args:
        profile: The student's immutable profile

    Returns:
        StudentDailyState with randomized values for the day
    """
    # Calculate money with Gaussian variance
    base_money = _get_base_money(profile)
    variance = base_money * MONEY_VARIANCE
    available_money = max(0.0, random.gauss(base_money, variance / 2))

    # Determine mood (healthy or junk)
    healthy_prob = _get_healthy_mood_probability(profile)
    mood = "healthy" if random.random() < healthy_prob else "junk"

    # Determine drowsiness
    is_drowsy = random.random() < DROWSINESS_CHANCE

    return StudentDailyState(
        student_id=profile.student_id,
        available_money=round(available_money, 2),
        mood=mood,
        is_drowsy=is_drowsy,
    )


def generate_daily_states(profiles: List[StudentProfile]) -> List[StudentDailyState]:
    """Generate daily states for all students.

    Args:
        profiles: List of student profiles

    Returns:
        List of StudentDailyState objects, one per student
    """
    return [generate_daily_state(profile) for profile in profiles]
