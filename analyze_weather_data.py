#!/usr/bin/env python3
"""
SQL Analysis of Weather Data
Demonstrates practical SQL skills using your collected weather data
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def connect_to_database():
    """Connect to your weather database"""
    return sqlite3.connect("output/weather.db")

def basic_sql_analysis():
    """Basic SQL queries every data engineer should know"""
    conn = connect_to_database()
    
    print("=== BASIC SQL ANALYSIS ===")
    
    # Query 1: Count total records
    print("\n1. Total weather records collected:")
    result = conn.execute("SELECT COUNT(*) as total_records FROM weather_data").fetchone()
    print(f"   Total records: {result[0]}")
    
    # Query 2: Average temperature
    print("\n2. Average temperature:")
    result = conn.execute("SELECT AVG(temp) as avg_temp FROM weather_data").fetchone()
    print(f"   Average temperature: {result[0]:.2f}°C")
    
    # Query 3: Highest and lowest temperatures
    print("\n3. Temperature extremes:")
    result = conn.execute("""
        SELECT 
            MAX(temp) as max_temp, 
            MIN(temp) as min_temp 
        FROM weather_data
    """).fetchone()
    print(f"   Highest: {result[0]}°C")
    print(f"   Lowest: {result[1]}°C")
    
    # Query 4: Weather conditions breakdown
    print("\n4. Weather conditions breakdown:")
    results = conn.execute("""
        SELECT 
            weather, 
            COUNT(*) as count,
            AVG(temp) as avg_temp
        FROM weather_data 
        GROUP BY weather
        ORDER BY count DESC
    """).fetchall()
    
    for weather, count, avg_temp in results:
        print(f"   {weather}: {count} times (avg temp: {avg_temp:.1f}°C)")
    
    conn.close()

def intermediate_sql_analysis():
    """Intermediate SQL queries for job interviews"""
    conn = connect_to_database()
    
    print("\n=== INTERMEDIATE SQL ANALYSIS ===")
    
    # Query 5: Daily temperature trends
    print("\n5. Daily temperature trends (last 7 days):")
    results = conn.execute("""
        SELECT 
            DATE(timestamp) as date,
            AVG(temp) as avg_temp,
            MAX(temp) as max_temp,
            MIN(temp) as min_temp,
            COUNT(*) as readings
        FROM weather_data 
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """).fetchall()
    
    for date, avg_temp, max_temp, min_temp, readings in results:
        print(f"   {date}: Avg {avg_temp:.1f}°C (Max: {max_temp:.1f}°C, Min: {min_temp:.1f}°C, Readings: {readings})")
    
    # Query 6: Temperature above/below average
    print("\n6. Readings above vs below average temperature:")
    results = conn.execute("""
        WITH avg_temp AS (
            SELECT AVG(temp) as overall_avg FROM weather_data
        )
        SELECT 
            CASE 
                WHEN temp > overall_avg THEN 'Above Average'
                ELSE 'Below Average'
            END as category,
            COUNT(*) as count
        FROM weather_data, avg_temp
        GROUP BY category
    """).fetchall()
    
    for category, count in results:
        print(f"   {category}: {count} readings")
    
    # Query 7: Most recent data quality check
    print("\n7. Data quality check:")
    results = conn.execute("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN temp IS NULL THEN 1 END) as missing_temp,
            COUNT(CASE WHEN humidity IS NULL THEN 1 END) as missing_humidity,
            COUNT(CASE WHEN timestamp IS NULL THEN 1 END) as missing_timestamp,
            MIN(timestamp) as oldest_record,
            MAX(timestamp) as newest_record
        FROM weather_data
    """).fetchone()
    
    total, missing_temp, missing_humidity, missing_timestamp, oldest, newest = results
    print(f"   Total records: {total}")
    print(f"   Missing temperature: {missing_temp}")
    print(f"   Missing humidity: {missing_humidity}")
    print(f"   Missing timestamps: {missing_timestamp}")
    print(f"   Data range: {oldest} to {newest}")
    
    conn.close()

def advanced_sql_analysis():
    """Advanced SQL for senior roles (you'll learn this later)"""
    conn = connect_to_database()
    
    print("\n=== ADVANCED SQL PREVIEW ===")
    
    # Query 8: Running average (window function)
    print("\n8. 3-reading moving average temperature:")
    results = conn.execute("""
        SELECT 
            timestamp,
            temp,
            AVG(temp) OVER (
                ORDER BY timestamp 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ) as moving_avg
        FROM weather_data 
        ORDER BY timestamp DESC
        LIMIT 10
    """).fetchall()
    
    for timestamp, temp, moving_avg in results:
        print(f"   {timestamp[:16]}: {temp}°C (3-point avg: {moving_avg:.1f}°C)")
    
    conn.close()

def export_for_visualization():
    """Export data for visualization step"""
    conn = connect_to_database()
    
    # Export daily summaries for charts
    df = pd.read_sql_query("""
        SELECT 
            DATE(timestamp) as date,
            AVG(temp) as avg_temp,
            MAX(temp) as max_temp,
            MIN(temp) as min_temp,
            AVG(humidity) as avg_humidity,
            weather
        FROM weather_data 
        GROUP BY DATE(timestamp), weather
        ORDER BY date DESC
    """, conn)
    
    df.to_csv("output/weather_analysis.csv", index=False)
    print(f"\n📊 Exported analysis data to output/weather_analysis.csv")
    print(f"📈 Ready for visualization step!")
    
    conn.close()
    return df

if __name__ == "__main__":
    print("🔍 ANALYZING YOUR WEATHER DATA WITH SQL")
    print("=" * 50)
    
    try:
        basic_sql_analysis()
        intermediate_sql_analysis()
        advanced_sql_analysis()
        
        print("\n" + "=" * 50)
        export_data = export_for_visualization()
        
        print(f"\n🎉 SQL Analysis Complete!")
        print(f"📋 This demonstrates SQL skills employers want:")
        print(f"   ✅ Data aggregation (COUNT, AVG, MAX, MIN)")
        print(f"   ✅ Grouping and filtering")
        print(f"   ✅ Date operations")
        print(f"   ✅ Data quality checks")
        print(f"   ✅ Window functions (advanced)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have weather data in output/weather.db")
        print("Run your ETL script first: python3 etl_production.py") 