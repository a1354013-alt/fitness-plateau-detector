"""backend/seed_data.py

Seeds the SQLite database with realistic health records for local testing.

Run:
  cd backend
  python seed_data.py

Notes:
- Uses the same database configuration as the API (`app.database`).
- If records already exist, the script exits without modifying data.
"""

from __future__ import annotations

import random
import sys
import os
from datetime import date, timedelta

# Add backend/ to sys.path so `app.*` imports work when running as a script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select

from app.database import DATABASE_URL, create_db_and_tables, engine
from app.models.health_record import HealthRecord

random.seed(42)

EXERCISE_TYPES = ["Running", "Cycling", "Walking", "Gym", "Swimming", "Yoga", "HIIT", "Rest"]


def generate_records(days: int = 30) -> list[dict]:
    records: list[dict] = []
    today = date.today()
    start_date = today - timedelta(days=days - 1)

    base_weight = 75.0

    for i in range(days):
        d = start_date + timedelta(days=i)
        weekday = d.weekday()  # 0=Mon, 6=Sun
        is_weekend = weekday >= 5

        # Weight trajectory
        if i < 10:
            # Losing phase
            weight = base_weight - (i * 0.2) + random.uniform(-0.15, 0.15)
        elif i < 20:
            # Plateau phase (minimal change)
            weight = 73.0 + random.uniform(-0.25, 0.25)
        else:
            # Slight rebound
            weight = 73.0 + (i - 20) * 0.05 + random.uniform(-0.2, 0.2)

        weight = round(weight, 1)

        # Sleep: some bad nights
        if i in [5, 12, 18, 24]:
            sleep = round(random.uniform(4.5, 5.5), 1)
        else:
            sleep = round(random.uniform(6.5, 8.5), 1)

        # Calories: weekends higher
        if is_weekend:
            calories = random.randint(2200, 2800)
        else:
            calories = random.randint(1700, 2100)

        protein = random.randint(80, 160)

        # Exercise: drop in plateau phase
        if i < 10:
            exercise_min = random.choice([30, 40, 45, 50, 60])
            exercise_type = random.choice(["Running", "Cycling", "HIIT", "Gym"])
        elif i < 20:
            exercise_min = random.choice([0, 0, 15, 20, 30])
            exercise_type = random.choice(["Walking", "Rest", "Rest", "Yoga"])
        else:
            exercise_min = random.choice([20, 30, 40, 45])
            exercise_type = random.choice(["Running", "Walking", "Gym"])

        steps = random.randint(4000, 12000)

        notes_pool = [
            "Feeling good today",
            "Tired after work",
            "Had a big dinner",
            "Skipped workout",
            "Great run this morning",
            "Stress eating",
            "Slept poorly",
            None,
            None,
            None,
        ]
        note = random.choice(notes_pool)

        records.append(
            {
                "record_date": d,
                "weight": weight,
                "sleep_hours": sleep,
                "calories": calories,
                "protein": protein,
                "exercise_minutes": exercise_min,
                "exercise_type": exercise_type,
                "steps": steps,
                "note": note,
            }
        )

    return records


def seed() -> None:
    print("Creating database tables...")
    create_db_and_tables()

    db_path_hint = DATABASE_URL.replace("sqlite:///", "")
    print(f"Database: {db_path_hint}")

    with Session(engine) as session:
        existing = session.exec(select(HealthRecord)).first()
        if existing:
            print("Database already has records. Skipping seed.")
            print("To re-seed, delete the SQLite file shown above and run again.")
            return

        records = generate_records(30)
        print(f"Inserting {len(records)} records...")

        for r in records:
            session.add(HealthRecord(**r))

        session.commit()

        print(f"Seeded {len(records)} health records successfully.")
        print(f"Date range: {records[0]['record_date']} -> {records[-1]['record_date']}")
        print(
            "Weight range: "
            f"{min(r['weight'] for r in records)} -> {max(r['weight'] for r in records)} kg"
        )


if __name__ == "__main__":
    seed()
