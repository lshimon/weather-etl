from config import API_KEY, CITY
import requests
import csv
import os
from datetime import datetime
import sqlite3
from datetime import timedelta
import pandas as pd


# Fetch weather data from OpenWeather API
def extract():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)  # send HTTP GET request
    data = response.json()        # convert JSON response to Python dict

    if response.status_code != 200:
        print("API ERROR:", data)
        return None

    return data

# Extract only relevant fields from the full API response
def transform(data):
    return {
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat(),
        "city": data["name"],
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["main"]
    }

# Save the transformed data to a CSV file
def load(data, filename="output/weather_data.csv"):
    file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0

    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()   # write column names

        writer.writerow(data)  # write one row of data

# ✅ Save the data into SQLite DB
def load_to_sqlite(data, db_name="output/weather.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            timestamp TEXT,
            city TEXT,
            temp REAL,
            humidity INTEGER,
            weather TEXT
        )
    """)

    # Insert the row
    cursor.execute("""
        INSERT INTO weather_data (timestamp, city, temp, humidity, weather)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["timestamp"],
        data["city"],
        data["temp"],
        data["humidity"],
        data["weather"]
    ))

    conn.commit()
    conn.close()


# Combine all ETL steps
def run():
    raw = extract()
    if raw is None:
        return
    processed = transform(raw)
    load(processed)
    load_to_sqlite(processed)
    print("Saved weather data:", processed)  # 👈 helpful confirmation message

# ✅ Query the data from the SQLite DB
def query_weather_data(db_name="output/weather.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Run a basic query: get all rows where temperature > 30
    cursor.execute("""
        SELECT timestamp, city, temp, humidity, weather
        FROM weather_data
        WHERE temp > 25
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    # Print the results nicely
    print("\n📊 HOT WEATHER RESULTS (>30°C):")
    for row in rows:
        print(row)

# ✅ Query rows between two timestamps
def query_by_date_range(start_date, end_date, db_name="output/weather.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Filter by timestamp range
    cursor.execute("""
        SELECT timestamp, city, temp, humidity, weather
        FROM weather_data
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp ASC
    """, (start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    print(f"\n📅 RESULTS BETWEEN {start_date} and {end_date}:")
    for row in rows:
        print(row)

# ✅ Query the last 24 hours
def query_last_24_hours(db_name="output/weather.db"):
    now = datetime.utcnow().replace(microsecond=0)
    yesterday = now - timedelta(hours=24)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, city, temp, humidity, weather
        FROM weather_data
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp ASC
    """, (yesterday.isoformat(), now.isoformat()))

    rows = cursor.fetchall()
    conn.close()

    print(f"\n🕒 RESULTS FROM LAST 24 HOURS ({yesterday} → {now}):")
    for row in rows:
        print(row)




if __name__ == "__main__":
    run()
    query_weather_data()
    query_by_date_range("2025-06-01T00:00:00", "2025-06-03T00:00:00")
    query_last_24_hours()
