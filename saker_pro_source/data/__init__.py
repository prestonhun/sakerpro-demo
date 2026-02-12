# saker_pro_source/data/__init__.py
"""Data loading and demo data generation."""

from .data_loader import load_workouts
from .demo_data import (
    generate_all_demo_data,
    generate_demo_workouts,
    generate_demo_activities,
    generate_demo_nutrition,
    generate_demo_weight,
    is_demo_data,
)

__all__ = [
    "load_workouts",
    "generate_all_demo_data",
    "generate_demo_workouts",
    "generate_demo_activities",
    "generate_demo_nutrition",
    "generate_demo_weight",
    "is_demo_data",
]
