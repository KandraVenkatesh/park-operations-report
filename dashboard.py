import sqlite3
import pandas as pd
import streamlit as st

st.title("Park Operations Daily Snapshot")
st.caption("All data is simulated.")

conn = sqlite3.connect("park.db")
df = pd.read_sql("SELECT * FROM park_daily", conn)
conn.close()
df["date"] = pd.to_datetime(df["date"])

chosen = st.date_input(
    "Choose a day",
    value=df["date"].max().date(),
    min_value=df["date"].min().date(),
    max_value=df["date"].max().date(),
)

day = df[df["date"] == pd.Timestamp(chosen)].iloc[0]

st.subheader(f"Date: {chosen}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Visitors", f"{day['visitors']:,}")
col2.metric("Avg wait (min)", day["avg_wait_min"])
col3.metric("Weather", day["weather"])
col4.metric("Staff", day["staff_count"])
st.subheader("Visitors vs average wait (all days)")
st.scatter_chart(df, x="visitors", y="avg_wait_min")
df["visitors_per_staff"] = df["visitors"] / df["staff_count"]
st.subheader("Visitors per staff member vs average wait")
st.scatter_chart(df, x="visitors_per_staff", y="avg_wait_min")
st.subheader("Staffing scenario (hypothesis only)")
extra = st.slider("Extra staff on the chosen day", 0, 20, 0)
new_ratio = day["visitors"] / (day["staff_count"] + extra)
similar = df[(df["visitors_per_staff"] - new_ratio).abs() <= 2]
st.write(f"Visitors per staff member would be about {new_ratio:.1f}.")
if len(similar) > 0:
    st.write(
        f"Simulated days with a similar ratio had an average wait of about "
        f"{similar['avg_wait_min'].mean():.0f} min ({len(similar)} days)."
    )
st.caption(
    "A hypothesis to review with the floor manager. Staff may not be freely "
    "movable because of training and safety rules."
)