import pandas as pd
import sqlite3
from datetime import datetime, timedelta   

# Step 1: Load CSV
df = pd.read_csv("output/weather_data.csv")  # Make sure the file exists in the same folder

# Step 2: Preview the data
print("Before cleaning:")
print(df.head())

# Step 3: Drop completely empty rows
df = df.dropna(how="all")

# Step 4: Convert 'Date' column to datetime (if exists)
if 'timestamp' in df.columns:
    # Only accept ISO format dates (the standard)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')
    # Add UTC timezone info
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')

# Step 5: Rename columns to snake_case
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Step 6: Save the cleaned file
df.to_csv("output/weather_cleaned.csv", index=False)

print("✅ Cleaning done. Saved as output/weather_cleaned.csv")

# Step 7: Load cleaned data back to database
conn = sqlite3.connect('output/weather.db')
df.to_sql('weather_data_clean', conn, if_exists='replace', index=False)
conn.close()

# ✅ Query the cleaned data
def query_cleaned_data(db_name="output/weather.db"):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, city, temp, humidity, weather
        FROM weather_data_clean
        ORDER BY timestamp ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    print(f"\n🕒 RESULTS FROM CLEANED DATA:")
    for row in rows:
        print(row)

if __name__ == "__main__":
    query_cleaned_data()