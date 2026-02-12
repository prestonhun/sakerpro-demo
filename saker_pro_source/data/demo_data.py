# demo_data.py
"""
Generates realistic demo data for the Saker Pro dashboard when no real
data has been uploaded.  All data is deterministic (seeded) so the demo
looks consistent across refreshes.
"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd


_RNG = np.random.RandomState(42)
random.seed(42)

# ---------------------------------------------------------------------------
# Exercise library for demo workouts
# ---------------------------------------------------------------------------
_EXERCISES = {
    "Push": [
        ("Bench Press (Barbell)", 185, 225),
        ("Overhead Press (Barbell)", 95, 135),
        ("Incline Dumbbell Press", 55, 80),
        ("Cable Flyes", 30, 50),
        ("Tricep Pushdown", 50, 80),
    ],
    "Pull": [
        ("Deadlift (Barbell)", 225, 365),
        ("Barbell Row", 135, 205),
        ("Pull Up", 0, 45),
        ("Face Pull", 30, 50),
        ("Barbell Curl", 55, 85),
    ],
    "Legs": [
        ("Squat (Barbell)", 185, 315),
        ("Romanian Deadlift (Barbell)", 165, 245),
        ("Leg Press", 270, 450),
        ("Leg Curl (Machine)", 80, 130),
        ("Calf Raise (Machine)", 135, 225),
    ],
    "Upper": [
        ("Bench Press (Barbell)", 185, 225),
        ("Barbell Row", 135, 205),
        ("Overhead Press (Barbell)", 95, 135),
        ("Pull Up", 0, 45),
        ("Dumbbell Curl", 30, 45),
    ],
    "Lower": [
        ("Squat (Barbell)", 185, 315),
        ("Romanian Deadlift (Barbell)", 165, 245),
        ("Leg Press", 270, 450),
        ("Leg Curl (Machine)", 80, 130),
        ("Calf Raise (Machine)", 135, 225),
    ],
}

_SPLIT_ROTATION = ["Push", "Pull", "Legs", "Push", "Pull", "Legs", "Upper"]

# ---------------------------------------------------------------------------
# Cardio / activities demo
# ---------------------------------------------------------------------------
_CARDIO_TYPES = [
    ("Running", 25, 55, 3.0, 7.0),   # (type, min_dur, max_dur, min_dist, max_dist)
    ("Cycling", 30, 75, 8.0, 25.0),
    ("Walking", 20, 45, 1.0, 3.5),
]


def generate_demo_workouts(days: int = 120) -> pd.DataFrame:
    """Generate a realistic Hevy-style workout DataFrame."""
    today = date.today()
    start = today - timedelta(days=days)
    rows: list[dict] = []

    split_idx = 0
    for day_offset in range(days):
        d = start + timedelta(days=day_offset)
        weekday = d.weekday()

        # Rest on Sundays and ~1 random day
        if weekday == 6 or (weekday == 3 and day_offset % 3 == 0):
            continue

        split = _SPLIT_ROTATION[split_idx % len(_SPLIT_ROTATION)]
        split_idx += 1

        exercises = _EXERCISES[split]
        start_time = datetime.combine(d, datetime.min.time().replace(hour=7, minute=30))
        end_time = start_time + timedelta(minutes=random.randint(50, 80))
        _workout_dur_s = (end_time - start_time).total_seconds()

        # Ramp volume in last 10 days so demo ACWR lands in "Peaking" (>1.1)
        _days_left = days - day_offset
        _volume_mult = 1.45 if _days_left <= 10 else 1.0

        for ex_name, w_low, w_high in exercises:
            n_sets = random.choice([4, 5, 5, 6]) if _days_left <= 10 else random.choice([3, 4, 4, 5])
            for s in range(n_sets):
                weight = round(random.uniform(w_low * _volume_mult, w_high * _volume_mult) / 5) * 5
                reps = random.choice([5, 6, 8, 8, 10, 10, 12])
                rpe = round(random.uniform(6.5, 9.5), 1)
                rows.append({
                    "title": split,
                    "start_time": start_time.strftime("%d %b %Y, %H:%M"),
                    "end_time": end_time.strftime("%d %b %Y, %H:%M"),
                    "exercise_title": ex_name,
                    "set_index": s,
                    "set_type": "normal",
                    "weight_lbs": weight,
                    "reps": reps,
                    "rpe": rpe,
                    "duration_seconds": _workout_dur_s / len(exercises),
                    "distance_miles": None,
                })

    df = pd.DataFrame(rows)
    # Run through the same normalisation as real data
    df["date"] = pd.to_datetime(df["start_time"], errors="coerce").dt.normalize()
    df["weight_kg"] = df["weight_lbs"] / 2.20462
    df["tonnage_lbs"] = df["weight_lbs"].fillna(0) * df["reps"].fillna(0)
    for col in ["weight_lbs", "weight_kg", "reps", "rpe", "duration_seconds", "distance_miles"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def generate_demo_activities(days: int = 120) -> pd.DataFrame:
    """Generate demo cardio / activity data."""
    today = date.today()
    start = today - timedelta(days=days)
    rows: list[dict] = []

    for day_offset in range(days):
        d = start + timedelta(days=day_offset)
        # ~4 cardio sessions per week
        if random.random() < 0.43:
            continue
        activity_type, min_dur, max_dur, min_dist, max_dist = random.choice(_CARDIO_TYPES)
        duration_min = round(random.uniform(min_dur, max_dur), 1)
        distance = round(random.uniform(min_dist, max_dist), 2)
        avg_hr = random.randint(125, 165)
        max_hr = avg_hr + random.randint(10, 30)
        calories = int(duration_min * random.uniform(8, 12))

        rows.append({
            "date": pd.Timestamp(d),
            "activity_type": activity_type,
            "duration_seconds": duration_min * 60,
            "duration_min": duration_min,
            "distance_miles": distance,
            "avg_hr": avg_hr,
            "max_hr": max_hr,
            "calories": calories,
        })

    return pd.DataFrame(rows)


def generate_demo_nutrition(days: int = 120) -> pd.DataFrame:
    """Generate demo daily nutrition data."""
    today = date.today()
    start = today - timedelta(days=days)
    rows: list[dict] = []

    for day_offset in range(days):
        d = start + timedelta(days=day_offset)
        _days_left = days - day_offset
        # Bump calories in last 10 days so demo diet shows "Bulking"
        _cal_base = 2900 if _days_left <= 10 else 2400
        cals = int(_RNG.normal(_cal_base, 150))
        protein = int(_RNG.normal(200 if _days_left <= 10 else 180, 20))
        carbs = int(_RNG.normal(300 if _days_left <= 10 else 250, 35))
        fat = int(_RNG.normal(95 if _days_left <= 10 else 80, 12))
        rows.append({
            "date": pd.Timestamp(d),
            "calories": max(cals, 1400),
            "protein_g": max(protein, 80),
            "carbs_g": max(carbs, 100),
            "fat_g": max(fat, 30),
        })

    return pd.DataFrame(rows)


def generate_demo_weight(days: int = 120) -> pd.DataFrame:
    """Generate demo body-weight trend."""
    today = date.today()
    start = today - timedelta(days=days)
    base_weight = 185.0
    rows: list[dict] = []

    for day_offset in range(days):
        d = start + timedelta(days=day_offset)
        # Slight downward trend with noise
        weight = base_weight - (day_offset * 0.03) + _RNG.normal(0, 0.6)
        rows.append({
            "date": pd.Timestamp(d),
            "weight_lbs": round(weight, 1),
        })

    return pd.DataFrame(rows)


def generate_all_demo_data(days: int = 120) -> dict:
    """
    Return dict with keys: workouts, activities, nutrition, weight.
    Each value is a DataFrame.
    """
    return {
        "workouts": generate_demo_workouts(days),
        "activities": generate_demo_activities(days),
        "nutrition": generate_demo_nutrition(days),
        "weight": generate_demo_weight(days),
    }


def is_demo_data(df: pd.DataFrame) -> bool:
    """Heuristic: demo workouts always have split-named titles."""
    if df is None or df.empty:
        return False
    if "title" in df.columns:
        titles = set(df["title"].dropna().unique())
        return titles.issubset({"Push", "Pull", "Legs", "Upper", "Lower"})
    return False
