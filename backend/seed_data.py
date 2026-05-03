from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, delete

from app.database import DATABASE_URL, create_db_and_tables, engine
from app.models.health_record import HealthRecord

random.seed(42)


def _base_record(d: date) -> dict:
    return {
        'record_date': d,
        'weight': 75.0,
        'sleep_hours': 7.0,
        'calories': 2000,
        'protein': 120,
        'exercise_minutes': 30,
        'exercise_type': 'Walking',
        'steps': 8000,
        'note': None,
    }


def scenario_healthy_progress(days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        r = _base_record(d)
        r['weight'] = round(78.0 - i * 0.12, 1)
        r['calories'] = 1800
        r['protein'] = 140
        rows.append(r)
    return rows


def scenario_plateau_case(days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        r = _base_record(d)
        r['weight'] = round(75.0 + random.uniform(-0.2, 0.2), 1)
        r['calories'] = 2250
        r['sleep_hours'] = 5.8
        rows.append(r)
    return rows


def scenario_missing_data_case(days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        if i % 5 == 0:
            continue
        rows.append(_base_record(d))
    return rows


def scenario_high_calorie_case(days: int = 30) -> list[dict]:
    start = date.today() - timedelta(days=days - 1)
    rows: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        r = _base_record(d)
        r['calories'] = 2800 if d.weekday() >= 5 else 2400
        r['weight'] = round(74.0 + i * 0.08, 1)
        rows.append(r)
    return rows


def scenario_demo_plateau() -> list[dict]:
    """A 21-day scenario: 7 days loss, 14 days plateau with clear causes."""
    today = date.today()
    rows: list[dict] = []

    # Week 1: Healthy progress (78kg -> 77.2kg)
    for i in range(7):
        d = today - timedelta(days=20 - i)
        r = _base_record(d)
        r['weight'] = round(78.0 - i * 0.12, 1)
        r['calories'] = 1800
        r['sleep_hours'] = 7.5
        r['exercise_minutes'] = 45
        rows.append(r)

    # Week 2-3: Plateau (stays around 77.2kg)
    # Causes: High calories, low sleep, weekend overeating
    for i in range(7, 21):
        d = today - timedelta(days=20 - i)
        r = _base_record(d)
        r['weight'] = round(77.2 + random.uniform(-0.1, 0.1), 1)

        # Weekend overeating (Friday, Saturday)
        if d.weekday() in (4, 5):
            r['calories'] = 2800
            r['note'] = "Social dinner, ate more than planned."
        else:
            r['calories'] = 2300  # Slightly over maintenance

        r['sleep_hours'] = 5.5
        r['exercise_minutes'] = 15
        rows.append(r)

    return rows


SCENARIOS = {
    'healthy_progress': scenario_healthy_progress,
    'plateau_case': scenario_plateau_case,
    'missing_data_case': scenario_missing_data_case,
    'high_calorie_case': scenario_high_calorie_case,
    'demo_plateau': scenario_demo_plateau,
}


def seed(scenario: str, clear: bool = True) -> None:
    create_db_and_tables()
    print(f'Database: {DATABASE_URL}')

    rows = SCENARIOS[scenario]()
    with Session(engine) as session:
        if clear:
            print("Clearing old records...")
            session.exec(delete(HealthRecord))
        for r in rows:
            session.add(HealthRecord(**r))
        session.commit()

    print(f'Seeded scenario={scenario} with {len(rows)} records.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', choices=sorted(SCENARIOS.keys()), default='demo_plateau')
    parser.add_argument('--no-clear', action='store_false', dest='clear', help='Do not clear existing records')
    args = parser.parse_args()
    seed(args.scenario, clear=args.clear)
