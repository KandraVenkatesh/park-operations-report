import sqlite3
import pandas as pd

conn = sqlite3.connect("park.db")
df = pd.read_sql("SELECT * FROM park_daily", conn)
conn.close()

df["date"] = pd.to_datetime(df["date"])

weekly = df.resample("W", on="date").agg(
    days=("visitors", "count"),
    total_visitors=("visitors", "sum"),
    total_sales=("ticket_sales", "sum"),
    avg_wait=("avg_wait_min", "mean"),
).round(1)

weekly["visitors_change_pct"] = (weekly["total_visitors"].pct_change() * 100).round(1)
weekly["visitors_per_day"] = (weekly["total_visitors"] / weekly["days"]).round(0)
weekly["per_day_change_pct"] = (weekly["visitors_per_day"].pct_change() * 100).round(1)
weekly["complete_week"] = weekly["days"] == 7

print(weekly.tail(5).to_string())

complete = weekly[weekly["complete_week"]]

report = weekly.reset_index()
report["date"] = report["date"].dt.strftime("%Y-%m-%d")
report = report.rename(columns={
    "date": "Week ending (Sun)",
    "days": "Days of data",
    "total_visitors": "Total visitors",
    "total_sales": "Ticket sales (JPY)",
    "avg_wait": "Avg wait (min)",
    "visitors_change_pct": "Visitors vs last week (%)",
    "visitors_per_day": "Visitors per day",
    "per_day_change_pct": "Per-day change (%)",
    "complete_week": "Complete week?",
})
report["Complete week?"] = report["Complete week?"].map({True: "Yes", False: "No - incomplete"})

summary = pd.DataFrame({
    "Item": [
        "Busiest complete week (week ending)",
        "Visitors in that week",
        "Longest average wait, week ending",
        "Longest average wait (min)",
        "Average visitors per day (complete weeks)",
        "Note",
    ],
    "Value": [
        complete["total_visitors"].idxmax().strftime("%Y-%m-%d"),
        f"{complete['total_visitors'].max():,}",
        complete["avg_wait"].idxmax().strftime("%Y-%m-%d"),
        complete["avg_wait"].max(),
        f"{complete['visitors_per_day'].mean():,.0f}",
        "All data is simulated. Incomplete weeks are excluded.",
    ],
})

with pd.ExcelWriter("weekly_report.xlsx", engine="openpyxl") as writer:
    report.to_excel(writer, index=False, sheet_name="Weekly")
    ws = writer.sheets["Weekly"]
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 24
    for row in ws.iter_rows(min_row=2):
        for i in (2, 3, 6):
            row[i].number_format = "#,##0"

    summary.to_excel(writer, index=False, sheet_name="Summary")
    writer.sheets["Summary"].column_dimensions["A"].width = 45
    writer.sheets["Summary"].column_dimensions["B"].width = 55

print("Saved weekly_report.xlsx")