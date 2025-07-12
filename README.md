# Weather ETL Pipeline & Dashboard

**What this demonstrates:** How to build a complete data pipeline from scratch - API integration, database design, scheduling, error handling, and data visualization.

## About This Project

I built this to learn ETL pipelines by creating something actually useful. It collects weather data from Tel Aviv every 10 minutes, stores it properly, and shows everything in a clean dashboard. The whole thing runs automatically and keeps track of data quality.

## What It Does

- **Grabs weather data** from OpenWeatherMap API every 10 minutes
- **Stores everything** in SQLite database with proper validation
- **Shows live dashboard** with temperature trends and system health
- **Runs automatically** via cron with full logging
- **Monitors data quality** - catches missing values, weird temperatures, duplicates

## Tech Stack

Python 3.9, SQLite, Matplotlib, OpenWeatherMap API, Cron scheduling

## Dashboard Features

1. **Temperature trends** over the last 5 days
2. **Today's summary** - min/max temps with reading counts
3. **Data freshness** - green if recent, red if something's wrong
4. **Quality report** - total records, any issues found

## How to Run

```bash
# Install what you need
pip install -r requirements.txt

# Add your API key
echo 'API_KEY = "your_key_here"' > config.py
echo 'CITY = "Tel Aviv"' >> config.py

# Test it manually
python3 etl_production.py

# See the dashboard
python3 dashboard.py
```

## What I Learned

- Building reliable ETL pipelines that actually work
- Handling API errors and data validation
- Creating automated scheduling with proper logging
- Building dashboards that show system health
- Managing database operations and data quality

Currently collecting 200+ weather records with perfect data quality.
