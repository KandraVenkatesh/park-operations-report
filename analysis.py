import sqlite3

conn = sqlite3.connect("park.db")

query = """
SELECT is_weekend,
       COUNT(*) AS days,
       ROUND(AVG(visitors)) AS avg_visitors,
       ROUND(AVG(avg_wait_min), 1) AS avg_wait
FROM park_daily
GROUP BY is_weekend
"""

for row in conn.execute(query):
    print(row)
print("--- Monthly ---")
monthly = """
SELECT strftime('%Y-%m', date) AS month,
       SUM(visitors) AS total_visitors,
       SUM(ticket_sales) AS total_sales
FROM park_daily
GROUP BY month
ORDER BY month
"""
for row in conn.execute(monthly):
    print(row)
print("--- Rain days per month ---")
check = """
SELECT strftime('%Y-%m', date) AS month,
       SUM(weather = 'Rain') AS rain_days,
       SUM(is_weekend) AS weekend_days
FROM park_daily
WHERE date < '2026-01-01'
GROUP BY month
ORDER BY month
"""
for row in conn.execute(check):
    print(row)
print("--- Top 5 busiest days ---")
top = """
SELECT date, visitors, weather, is_holiday, is_weekend, avg_wait_min
FROM park_daily
ORDER BY visitors DESC
LIMIT 5
"""
for row in conn.execute(top):
    print(row)
print("--- Days with wait over 60 min ---")
long_wait = """
SELECT is_holiday,
       COUNT(*) AS days
FROM park_daily
WHERE avg_wait_min > 60
GROUP BY is_holiday
"""
for row in conn.execute(long_wait):
    print(row)
print("--- Long-wait rate ---")
rate = """
SELECT is_holiday,
       COUNT(*) AS total_days,
       SUM(avg_wait_min > 60) AS long_days,
       ROUND(100.0 * SUM(avg_wait_min > 60) / COUNT(*), 1) AS pct
FROM park_daily
GROUP BY is_holiday
"""
for row in conn.execute(rate):
    print(row)
conn.close()