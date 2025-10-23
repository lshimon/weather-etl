import os
import sys
from datetime import datetime
from config import API_KEY, CITY
import requests
import csv
import sqlite3
from google.cloud import bigquery

# ==================================
# BigQuery Configuration
# !! You will update this path on your new computer !!
SERVICE_ACCOUNT_PATH = "/path/to/your/service_account.json" 

# !! Update this with your actual GCP Project ID !!
BIGQUERY_PROJECT_ID = "your-gcp-project-id" 
BIGQUERY_DATASET_ID = "weather_db" # This is the Dataset name we will create
BIGQUERY_TABLE_ID = "weather_data" # This is the Table name we will create

# Set the environment variable so Google's library can find the key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
# ==================================

# Set absolute paths for cron execution
BASE_PATH = "/usr/local/weather-etl"

# Add current directory to Python path
sys.path.insert(0, BASE_PATH)

def log_message(message):
    """Add timestamp to all log messages"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def extract():
    """Fetch weather data from OpenWeather API"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            log_message(f"API ERROR: {data}")
            return None
            
        log_message("✅ API call successful")
        return data
        
    except Exception as e:
        log_message(f"❌ API call failed: {e}")
        return None

def transform(data):
    """Extract relevant fields from API response"""

    # Discovered during initial runs that the API sometimes sends temperature as a string.
    # So I added explicit casting to float to prevent database type errors.
    temp_value = float(data["main"]["temp"])

    return {
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "+00:00",
        "city": data["name"],
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["main"]
    }

def load_to_csv(data, filename=f"{BASE_PATH}/output/weather_data.csv"):
    """Save data to CSV file"""
    try:
        file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
        
        with open(filename, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(data)
            
        log_message(f"✅ Data saved to CSV: {filename}")
        return True
        
    except Exception as e:
        log_message(f"❌ CSV save failed: {e}")
        return False

def load_to_sqlite(data, db_name=f"{BASE_PATH}/output/weather.db"):
    """Save data to SQLite database"""
    try:
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
        
        log_message(f"✅ Data saved to SQLite: {db_name}")
        return True
        
    except Exception as e:
        log_message(f"❌ SQLite save failed: {e}")
        return False

def load_to_bigquery(data, client):
    """Loads the processed data row into the BigQuery table."""
    
    try:
        # 1. Define the full table 'address'
        table_full_id = f"{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{BIGQUERY_TABLE_ID}"
        
        # 2. BigQuery expects a list of rows, even if we send only one.
        rows_to_insert = [data] 
        
        # 3. This is the command to send the data
        errors = client.insert_rows_json(table_full_id, rows_to_insert)  
        
        # 4. Check if the command worked
        if errors == []:
            # Success!
            log_message("SUCCESS", f"Data loaded to BigQuery table {table_full_id}")
            return True
        else:
            # Failure. The API returned errors.
            log_message("ERROR", f"Failed to load data to BigQuery: {errors}")
            return False
            
    except Exception as e:
        # Failure. Something else broke (like bad credentials, no internet, etc.)
        log_message("ERROR", f"Exception during BigQuery load: {e}")
        return False

def validate_data(data):
    """
    Validate weather data before saving
    Returns: (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['temp', 'humidity', 'weather']
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Missing required field: {field}"
    
    # Check temperature range for validity
    if not (-5 <= data['temp'] <= 50):
        return False, f"Temperature {data['temp']}°C is outside reasonable range"
    
    # Check humidity range (0-100%)
    if not (0 <= data['humidity'] <= 100):
        return False, f"Humidity {data['humidity']}% is outside valid range"
    
    # Check weather field is not empty
    if not data['weather'] or data['weather'].strip() == '':
        return False, "Weather condition is empty"
    
    return True, "Data is valid"

def run_etl():
    """Main ETL process with data quality validation"""
    log_message("🚀 Starting Weather ETL (Production Mode)")
    
    # Extract
    raw_data = extract()
    if raw_data is None:
        log_message("❌ ETL failed: No data extracted")
        return False
    
    # Transform
    try:
        processed_data = transform(raw_data)
        log_message(f"✅ Data transformed: {processed_data['temp']}°C, {processed_data['humidity']}% humidity")
    except Exception as e:
        log_message(f"❌ Transform failed: {e}")
        return False
    

    # Validate
    is_valid, error_message = validate_data(processed_data)
    if not is_valid:
        log_message(f"❌ Data validation failed: {error_message}")
        log_message("⚠️ Skipping this record to maintain data quality")
        return False
    
    log_message("✅ Data validation passed")
    
    # Load
    csv_success = load_to_csv(processed_data)
    db_success = load_to_sqlite(processed_data)
    
    if csv_success and db_success:
        log_message("🎉 ETL completed successfully!")
        return True
    else:
        log_message("⚠️ ETL completed with some failures")
        return False

if __name__ == "__main__":
    success = run_etl()
    # Exit with proper code for cron monitoring
    sys.exit(0 if success else 1) 