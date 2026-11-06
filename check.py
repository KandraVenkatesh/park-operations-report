import sqlite3

conn = sqlite3.connect("park.db")

total = conn.execute(
    "SELECT SUM(visitors) FROM park_daily "
    "WHERE date BETWEEN '2025-04-28' AND '2025-05-04'"
).fetchone()[0]

print("Visitors, 2025-04-28 to 2025-05-04:", total)
conn.close()