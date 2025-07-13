# End-to-End Weather ETL Pipeline with SQL Analytics and Dashboard

A production-ready data engineering project demonstrating automated ETL pipeline design, data quality monitoring, and analytics dashboard development. This project showcases core data engineering skills including API integration, database design, scheduled automation, and data visualization.

## Project Overview

This project implements a complete ETL pipeline that extracts weather data from the OpenWeatherMap API, transforms and validates the data using Python, and loads it into a SQLite database for analysis. The pipeline runs every 10 minutes via cron and has collected 210+ weather records to date, with full data quality monitoring.

The system includes advanced SQL analytics with window functions, data quality checks for missing values and outliers, and a multi-panel matplotlib dashboard that provides up-to-date insights into weather patterns and system health. Built with production practices including structured logging, error handling, and absolute path management for cron execution.

## Architecture Diagram

```
OpenWeatherMap API
        ↓
Python ETL Script
        ↓
SQLite Database
        ↓
SQL Analysis
        ↓
Matplotlib Dashboard
```

## Key Features

### **Automated ETL Pipeline**
- Scheduled data extraction every 10 minutes via cron
- Robust error handling with comprehensive logging
- Production-ready deployment at `/usr/local/weather-etl/`

### **Data Engineering Best Practices**
- Data validation and quality checks (missing values, outliers, duplicates)
- Structured logging with timestamps and status indicators
- Absolute path management for cron execution
- Modular code architecture with separate ETL functions

### **Advanced SQL Analytics**
- Complex aggregations and window functions
- Time-based data analysis (daily summaries, trend analysis)
- Data quality monitoring queries
- Efficient indexing and query optimization

### **Dashboard & Insights**
- Multi-panel visualization showing temperature trends
- System health monitoring with data freshness indicators
- Daily min/max temperature summaries with reading counts
- Data quality metrics

### **Data Quality Monitoring**
- Automated validation of temperature ranges
- Missing value detection and reporting
- Duplicate record identification
- Automated data freshness monitoring

## Technologies Used

**Core Technologies:**
- **Python 3.9** - ETL logic and data processing
- **SQLite** - Local database for structured data storage
- **SQL** - Complex queries, aggregations, and analytics
- **Matplotlib** - Multi-panel dashboard visualization
- **Cron** - Automated scheduling and job management

**APIs & External Services:**
- **OpenWeatherMap API** - Real-time weather data source

**Development Tools:**
- **Git** - Version control and project management
- **Structured Logging** - Production-ready monitoring

## Screenshots
**Dashboard:**
![Weather Dashboard](https://github.com/user-attachments/assets/b54985eb-ef20-4a75-8d72-09b6f08d333d)

*Multi-panel dashboard showing temperature trends, daily summaries, and data quality metrics*


**Logs:**

Success: 

![ETL Logging Success](https://github.com/user-attachments/assets/33b3da2f-f361-4c55-9c2b-3fcfac6fa730)

Failed:

![ETL Logging Failed](https://github.com/user-attachments/assets/dd46592a-56e5-4e93-9a56-bc03f2054db7)

*Structured logging output showing successful ETL execution with timestamps*

## How to Run

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Create config file
echo 'API_KEY = "your_openweathermap_api_key"' > config.py
echo 'CITY = "Tel Aviv"' >> config.py
```

### Manual Execution

```bash
# Run ETL process once
python3 etl_production.py

# View dashboard
python3 dashboard.py

# Run SQL analytics
python3 analyze_weather_data.py
```

### Automated Scheduling

```bash
# Add to crontab for automated execution
*/10 * * * * /usr/bin/python3 /usr/local/weather-etl/etl_production.py >> /usr/local/weather-etl/cron.log 2>&1
```

## Database Schema

```sql
-- SQLite table structure
CREATE TABLE weather_data (
    timestamp TEXT,
    city TEXT,
    temp REAL,
    humidity INTEGER,
    weather TEXT
);

-- Example queries
SELECT DATE(timestamp) as date, AVG(temp) as avg_temp 
FROM weather_data 
GROUP BY DATE(timestamp) 
ORDER BY date DESC;
```

## Data Quality Metrics

Current pipeline status:
- **Total Records:** 210
- **Data Quality:** 100% (0 missing values, 0 outliers, 0 duplicates)
- **Automation:** Running successfully every 10 minutes via cron

## Future Scope / Learning Path

This project serves as a foundation for expanding into modern cloud-native data engineering tools:

### **Next Phase: Cloud Migration**
- **Data Warehousing:** Load to BigQuery / Snowflake / Redshift
- **Orchestration:** Replace cron with Apache Airflow / Prefect
- **Data Modeling:** Implement dbt for transformation layer
- **Cloud Storage:** Migrate to GCS / S3 for scalable storage

### **Advanced Features**
- **Stream Processing:** Real-time data with Apache Kafka
- **Data Lakehouse:** Delta Lake / Apache Iceberg architecture
- **MLOps Integration:** Feature stores and model serving
- **Infrastructure as Code:** Terraform for cloud deployment

### **Enhanced Analytics**
- **Business Intelligence:** Tableau / Power BI integration
- **Data Catalog:** Implement metadata management
- **Monitoring:** Prometheus / Grafana for production monitoring
- **Testing:** Great Expectations for data quality testing

## Architecture Decisions

### Why SQLite?
- Lightweight for local development and learning
- ACID compliance for data integrity
- Easy deployment without external dependencies
- Demonstrates SQL skills transferable to any database

### Why Cron?
- Unix-standard scheduling for reliability
- Simple deployment and monitoring
- Foundation for understanding job orchestration
- Production-ready for small to medium workloads

### Why Local First?
- Demonstrates core concepts without cloud complexity
- Cost-effective learning and development
- Easily adaptable to cloud environments
- Shows understanding of fundamental data engineering principles

---

This project demonstrates production-ready data engineering skills and serves as a stepping stone toward cloud-native data platforms.
