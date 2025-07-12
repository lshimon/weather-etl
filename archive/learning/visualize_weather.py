#!/usr/bin/env python3
import sqlite3
import matplotlib.pyplot as plt

def connect_to_database():
    return sqlite3.connect("/usr/local/weather-etl/output/weather.db")

def get_temperature_data():
    conn = connect_to_database()
    results = conn.execute("SELECT timestamp, temp FROM weather_data ORDER BY timestamp").fetchall()
    conn.close()
    return results

def create_temperature_chart():
    # Get the data
    data = get_temperature_data()
    
    # Separate timestamps and temperatures
    timestamps = [row[0] for row in data]
    temperatures = [row[1] for row in data]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, temperatures, marker='o')
    plt.title("Tel Aviv Temperature Over Time")
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    create_temperature_chart()




