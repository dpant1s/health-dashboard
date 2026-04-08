import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

DB_PATH = "habits.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            date TEXT PRIMARY KEY,
            sleep_hours REAL NOT NULL,
            workout_done INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()
def upsert_habit(entry_date, sleep_hours, workout_done):
    conn=get_conn()
    conn.execute("""
    INSERT INTO habits (date, sleep_hours, workout_done)
    VALUES (?,?,?)
    ON CONFLICT(date) DO UPDATE SET
    sleep_hours = excluded.sleep_hours,
    workout_done = excluded.workout_done
    """, (entry_date, sleep_hours, workout_done))
    conn.commit()
    conn.close()
def load_habits():
    conn = get_conn()
    df= pd.read_sql_query("SELECT * FROM habits ORDER BY date", conn)
    conn.close()
    return df
st.title("Habit & Health Insights Dashboard")
st.subheader("Welcome! xoxo")
date_input= st.date_input("Select Date")
sleep_input= st.number_input(
    "Hours of sleep",
    min_value=0.0,
    max_value=24.0,
    step=0.1
)
workout_input= st.checkbox("Did you workout today?")
if st.button("Save Entry"):
    if sleep_input <= 5:
        st.warning("Consider re-checking your sleep hours")
    else:
        upsert_habit(
            entry_date=date_input.strftime("%Y-%m-%d"),
            sleep_hours=float(sleep_input),
            workout_done=1 if workout_input else 0
        )
        st.success("Saved to database!")
st.subheader("Your Logged Data")
habits_df = load_habits()
habits_df["date"]= pd.to_datetime(habits_df["date"])
habits_df = habits_df.sort_values("date")
habits_df["rolling_7d_avg_sleep"]= habits_df["sleep_hours"].rolling(window=7, min_periods=1).mean()   
if not habits_df.empty:
    avg_sleep = habits_df["sleep_hours"].mean()
    workout_days = habits_df["workout_done"].sum()
    total_days = len(habits_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Days Logged", total_days)
    with col2:
        st.metric("Average Sleep", round(avg_sleep, 1))
    with col3:
        st.metric("Total Workout Days", workout_days)
    st.dataframe(habits_df)
    plt.figure()
    plt.plot(habits_df["date"], habits_df["sleep_hours"])
    plt.xticks(rotation=45)
    plt.axhline(y=8, color="pink", label="that's the minimum you've to get for healthy lifestyle")
    plt.legend()
    st.pyplot(plt)
    st.download_button(
        label="Download the data",
        data=habits_df.to_csv(index=False),
        file_name="habits.csv"
    )
else: 
    st.info ("no data logged yet.")




