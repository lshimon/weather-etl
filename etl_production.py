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
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather-etl-476111-68b860a4d4a2.json")

# !! Update this with your actual GCP Project ID !!
BIGQUERY_PROJECT_ID = "weather-etl-476111" 
BIGQUERY_DATASET_ID = "weather_db" # This is the Dataset name we will create
BIGQUERY_TABLE_ID = "weather_data" # This is the Table name we will create

# Set the environment variable so Google's library can find the key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH
# ==================================

# Set absolute paths for cron execution
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

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
            log_message(f"✅ Data loaded to BigQuery table {table_full_id}")
            return True
        else:
            # Failure. The API returned errors.
            log_message(f"❌ Failed to load data to BigQuery: {errors}")
            return False
            
    except Exception as e:
        # Failure. Something else broke (like bad credentials, no internet, etc.)
        log_message(f"❌ Exception during BigQuery load: {e}")
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
    
# PREPARE BigQuery 
    # Initialize BigQuery client
    try:
        bigquery_client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
        log_message("✅ Connected to BigQuery")
        
        # Create dataset if it doesn't exist
        dataset_ref = bigquery_client.dataset(BIGQUERY_DATASET_ID)
        try:
            bigquery_client.get_dataset(dataset_ref)
            log_message(f"✅ Dataset {BIGQUERY_DATASET_ID} already exists")
        except Exception:
            # Dataset doesn't exist, create it
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"  # Specify the location
            dataset = bigquery_client.create_dataset(dataset)
            log_message(f"✅ Created dataset {BIGQUERY_DATASET_ID}")
        
        # Create table if it doesn't exist
        table_ref = dataset_ref.table(BIGQUERY_TABLE_ID)
        try:
            bigquery_client.get_table(table_ref)
            log_message(f"✅ Table {BIGQUERY_TABLE_ID} already exists")
        except Exception:
            # Table doesn't exist, create it
            schema = [
                bigquery.SchemaField("timestamp", "TIMESTAMP"),
                bigquery.SchemaField("city", "STRING"),
                bigquery.SchemaField("temp", "FLOAT"),
                bigquery.SchemaField("humidity", "INTEGER"),
                bigquery.SchemaField("weather", "STRING")
            ]
            table = bigquery.Table(table_ref, schema=schema)
            table = bigquery_client.create_table(table)
            log_message(f"✅ Created table {BIGQUERY_TABLE_ID}")
        bigquery_success = True
    except Exception as e:
        log_message(f"❌ BigQuery setup failed: {e}")
        bigquery_success = False
    
    # Load
    csv_success = load_to_csv(processed_data)
    db_success = load_to_sqlite(processed_data)

    # Only attempt BigQuery load if setup was successful
    if 'bigquery_success' not in locals() or bigquery_success:
        bigquery_success = load_to_bigquery(processed_data, bigquery_client)
    
    if bigquery_success:
        log_message("🎉 ETL completed successfully with BigQuery integration!")
        return True
    else:
        log_message("⚠️ ETL completed with some failures")
        return False

if __name__ == "__main__":
    success = run_etl()
    # Exit with proper code for cron monitoring
    sys.exit(0 if success else 1) 