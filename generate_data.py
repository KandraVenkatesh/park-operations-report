"""
Module 1: Synthetic data generator for the Park Operations Daily Report Tool.

ALL DATA IS SIMULATED. The rules below are chosen by me, so any pattern in the
data is built in on purpose. It is used to practise the method, not to claim
real findings.
"""
import random
import sqlite3
from datetime import date, timedelta

random.seed(42)  # fixed seed so results are repeatable

DB_FILE = "park.db"
START = date(2025, 1, 1)
END = date(2026, 10, 31)

# Simplified list of some Japanese public holidays (not complete, for simulation only)
HOLIDAYS = {
    date(2025, 1, 1), date(2025, 1, 13), date(2025, 2, 11), date(2025, 4, 29),
    date(2025, 5, 3), date(2025, 5, 4), date(2025, 5, 5), date(2025, 7, 21),
    date(2025, 8, 11), date(2025, 9, 15), date(2025, 10, 13), date(2025, 11, 3),
    date(2026, 1, 1), date(2026, 1, 12), date(2026, 2, 11), date(2026, 4, 29),
    date(2026, 5, 3), date(2026, 5, 4), date(2026, 5, 5), date(2026, 7, 20),
    date(2026, 8, 11), date(2026, 9, 21), date(2026, 10, 12),
}

BASE_VISITORS = 5000
AVG_TICKET_YEN = 6000


def pick_weather():
    """Rule: 60% sunny, 25% cloudy, 15% rain."""
    r = random.random()
    if r < 0.60:
        return "Sunny"
    if r < 0.85:
        return "Cloudy"
    return "Rain"


def generate_day(d):
    is_weekend = 1 if d.weekday() >= 5 else 0
    is_holiday = 1 if d in HOLIDAYS else 0
    weather = pick_weather()

    # Rule 1: visitors depend on weekend, holiday and weather, plus random noise
    visitors = BASE_VISITORS
    if is_weekend:
        visitors *= 1.4
    if is_holiday:
        visitors *= 1.5
    if weather == "Rain":
        visitors *= 0.5
    elif weather == "Cloudy":
        visitors *= 0.95
    visitors *= random.uniform(0.85, 1.15)
    visitors = int(visitors)

    # Rule 2: more staff are scheduled on busy days (weekend/holiday)
    staff = random.randint(60, 75)
    if is_weekend or is_holiday:
        staff += random.randint(10, 20)

    # Rule 3: wait time rises with visitors per staff member, plus noise
    visitors_per_staff = visitors / staff
    avg_wait = max(5.0, (visitors_per_staff - 50) * 1.2 + random.uniform(-4, 4))
    avg_wait = round(avg_wait, 1)

    # Rule 4: ticket sales = visitors x average ticket price (with small variation)
    ticket_sales = int(visitors * AVG_TICKET_YEN * random.uniform(0.9, 1.1))

    return (d.isoformat(), visitors, ticket_sales, weather,
            is_holiday, is_weekend, staff, avg_wait)


def create_table(conn):
    conn.execute("DROP TABLE IF EXISTS park_daily")
    conn.execute("""
        CREATE TABLE park_daily (
            date          TEXT PRIMARY KEY,
            visitors      INTEGER NOT NULL,
            ticket_sales  INTEGER NOT NULL,
            weather       TEXT NOT NULL,
            is_holiday    INTEGER NOT NULL,
            is_weekend    INTEGER NOT NULL,
            staff_count   INTEGER NOT NULL,
            avg_wait_min  REAL NOT NULL
        )
    """)


def main():
    rows = []
    d = START
    while d <= END:
        rows.append(generate_day(d))
        d += timedelta(days=1)

    conn = sqlite3.connect(DB_FILE)
    create_table(conn)
    conn.executemany("INSERT INTO park_daily VALUES (?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()
    print(f"Created {DB_FILE} with {len(rows)} days of simulated data.")


if __name__ == "__main__":
    main()