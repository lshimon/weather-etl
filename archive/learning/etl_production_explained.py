#!/usr/bin/env python3
# ↑ SHEBANG LINE: Tells system "use Python 3 to run this script"
# Why needed: When cron runs this file, it needs to know which program to use

"""
Production Weather ETL Script for Cron
Runs automatically every 30 minutes via cron job
"""
# ↑ DOCSTRING: Documentation explaining what this script does

# IMPORT SECTION - Get tools we need
import os          # For changing directories, checking files
import sys         # For system operations, exit codes
from datetime import datetime  # For timestamps in logs

# CRITICAL SECTION: Set up paths for cron
# Problem: When YOU run script, terminal knows where you are
# Problem: When CRON runs script, it has no idea where your project is!

SCRIPT_DIR = "/Users/shimonleizerovich/Documents/weather-etl/weather-etl"
# ↑ ABSOLUTE PATH: Exact location of your project
# Why absolute: Cron doesn't know about "current directory"

os.chdir(SCRIPT_DIR)
# ↑ CHANGE DIRECTORY: Tell Python "go to this exact location"
# Why needed: So Python can find your config.py and output/ folder

sys.path.insert(0, SCRIPT_DIR)
# ↑ ADD TO PYTHON PATH: Tell Python "look for modules in this directory"
# Why needed: So "from config import API_KEY" works

# NOW we can import our project files
from config import API_KEY, CITY  # Our API key and city setting
import requests  # For making HTTP calls to weather API
import csv      # For saving data to CSV files
import sqlite3  # For saving data to database

def log_message(message):
    """Add timestamp to all log messages"""
    # Get current time in readable format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Print with timestamp prefix
    print(f"[{timestamp}] {message}")
    # Why needed: When cron runs, you need to know WHEN things happened

def extract():
    """Fetch weather data from OpenWeather API"""
    # Build the API URL with our city and key
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    
    try:
        # TRY BLOCK: Attempt the API call, be ready for problems
        response = requests.get(url, timeout=10)
        # ↑ timeout=10: Don't wait forever if API is slow
        
        data = response.json()  # Convert JSON response to Python dictionary
        
        # Check if API call was successful
        if response.status_code != 200:
            # 200 = success, anything else = problem
            log_message(f"API ERROR: {data}")
            return None  # Return nothing if failed
            
        log_message("✅ API call successful")
        return data  # Return the weather data
        
    except Exception as e:
        # EXCEPT BLOCK: If ANY error happens, catch it
        log_message(f"❌ API call failed: {e}")
        return None
        # Why needed: Network problems, timeouts, etc. shouldn't crash script

def transform(data):
    """Extract relevant fields from API response"""
    # Take the messy API response and pull out just what we need
    return {
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "+00:00",
        # ↑ Current time in UTC, ISO format (production standard)
        "city": data["name"],           # City name from API
        "temp": data["main"]["temp"],   # Temperature in Celsius  
        "humidity": data["main"]["humidity"],  # Humidity percentage
        "weather": data["weather"][0]["main"]  # Weather condition (Clear, Rain, etc.)
    }

def load_to_csv(data, filename="output/weather_data.csv"):
    """Save data to CSV file"""
    try:
        # Check if file already exists and has content
        file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
        
        # Open file in APPEND mode (add to end, don't overwrite)
        with open(filename, mode="a", newline="") as file:
            # Create CSV writer that knows our column names
            writer = csv.DictWriter(file, fieldnames=data.keys())
            
            # If file is new/empty, write column headers first
            if not file_exists:
                writer.writeheader()
            
            # Write our data as a new row
            writer.writerow(data)
            
        log_message(f"✅ Data saved to CSV: {filename}")
        return True  # Success
        
    except Exception as e:
        # If file writing fails, log the error
        log_message(f"❌ CSV save failed: {e}")
        return False  # Failure

def load_to_sqlite(data, db_name="output/weather.db"):
    """Save data to SQLite database"""
    try:
        # Connect to database (creates file if doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()  # Cursor = tool for executing SQL commands
        
        # Create table if it doesn't exist yet
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_data (
                timestamp TEXT,
                city TEXT,
                temp REAL,
                humidity INTEGER,
                weather TEXT
            )
        """)
        
        # Insert our new data row
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
        # ↑ ? placeholders prevent SQL injection attacks (security)
        
        conn.commit()  # Save changes to database
        conn.close()   # Close connection to free resources
        
        log_message(f"✅ Data saved to SQLite: {db_name}")
        return True
        
    except Exception as e:
        log_message(f"❌ SQLite save failed: {e}")
        return False

def run_etl():
    """Main ETL process with error handling"""
    log_message("🚀 Starting Weather ETL (Production Mode)")
    
    # EXTRACT PHASE
    raw_data = extract()
    if raw_data is None:
        # If extract failed, stop the whole process
        log_message("❌ ETL failed: No data extracted")
        return False
    
    # TRANSFORM PHASE
    try:
        processed_data = transform(raw_data)
        log_message(f"✅ Data transformed: {processed_data['temp']}°C, {processed_data['humidity']}% humidity")
    except Exception as e:
        log_message(f"❌ Transform failed: {e}")
        return False
    
    # LOAD PHASE (save to both CSV and database)
    csv_success = load_to_csv(processed_data)
    db_success = load_to_sqlite(processed_data)
    
    # Check if both saves worked
    if csv_success and db_success:
        log_message("🎉 ETL completed successfully!")
        return True
    else:
        log_message("⚠️ ETL completed with some failures")
        return False

# MAIN EXECUTION BLOCK
if __name__ == "__main__":
    # This only runs when script is executed directly (not imported)
    success = run_etl()
    
    # Exit with proper code for cron monitoring
    # 0 = success, 1 = failure (standard Unix convention)
    sys.exit(0 if success else 1) 