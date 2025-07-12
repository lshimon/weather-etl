import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta

def get_last_update():
    conn = sqlite3.connect("/usr/local/weather-etl/output/weather.db")
    result = conn.execute("SELECT MAX(timestamp) FROM weather_data").fetchone()
    conn.close()
    
    if result[0]:
        from datetime import timezone, timedelta
        # Parse the UTC timestamp
        dt = datetime.fromisoformat(result[0].replace('+00:00', ''))
        # Convert to UTC+3
        local_dt = dt + timedelta(hours=3)
        return local_dt.strftime("%b %d, %Y %I:%M %p")
    return "No data"

def get_temperature_trend():
    conn = sqlite3.connect("/usr/local/weather-etl/output/weather.db")
    # Get last 5 days of data
    result = conn.execute("""
        SELECT DATE(timestamp) as date, AVG(temp) as avg_temp
        FROM weather_data 
        WHERE timestamp >= datetime('now', '-5 days')
        GROUP BY DATE(timestamp)
        ORDER BY date
    """).fetchall()
    conn.close()
    return result

def get_today_summary():
    conn = sqlite3.connect("/usr/local/weather-etl/output/weather.db")
    result = conn.execute("""
        SELECT MIN(temp) as min_temp, MAX(temp) as max_temp, COUNT(*) as readings
        FROM weather_data 
        WHERE DATE(timestamp) = DATE('now')
    """).fetchone()
    conn.close()
    return result

def check_data_freshness():
    conn = sqlite3.connect("/usr/local/weather-etl/output/weather.db")
    result = conn.execute("""
        SELECT timestamp FROM weather_data 
        ORDER BY timestamp DESC LIMIT 1
    """).fetchone()
    conn.close()
    
    if result:
        from datetime import datetime, timedelta
        # Parse UTC timestamp
        last_update = datetime.fromisoformat(result[0].replace('+00:00', ''))
        # Convert to UTC+3
        last_update_local = last_update + timedelta(hours=3)
        
        # Get current local time
        now_local = datetime.utcnow() + timedelta(hours=3)
        
        # Calculate difference
        minutes_ago = (now_local - last_update_local).total_seconds() / 60
        return minutes_ago <= 30
    return False

def get_data_quality_report():
    conn = sqlite3.connect("/usr/local/weather-etl/output/weather.db")
    
    # Check 1: Missing values
    missing_check = conn.execute("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN temp IS NULL THEN 1 END) as missing_temp,
            COUNT(CASE WHEN humidity IS NULL THEN 1 END) as missing_humidity
        FROM weather_data
    """).fetchone()
    
    # Check 2: Outliers 
    outlier_check = conn.execute("""
        SELECT COUNT(*) as outliers
        FROM weather_data 
        WHERE temp < 0 OR temp > 50
    """).fetchone()
    
    # Check 3: Duplicate records (same timestamp)
    duplicate_check = conn.execute("""
        SELECT COUNT(*) - COUNT(DISTINCT timestamp) as duplicates
        FROM weather_data
    """).fetchone()
    
    conn.close()
    
    return {
        'total_records': missing_check[0],
        'missing_temp': missing_check[1],
        'missing_humidity': missing_check[2],
        'outliers': outlier_check[0],
        'duplicates': duplicate_check[0]
    }

# Create dashboard
fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(12, 10))


last_update = get_last_update()
ax1.text(0.5, 0.5, f"Last Update: {last_update}", 
         ha='center', va='center', fontsize=12, fontweight='bold')
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.axis('off')

# Panel 2: Temperature Trend
trend_data = get_temperature_trend()
if trend_data:
    dates = [row[0] for row in trend_data]
    temps = [row[1] for row in trend_data]
    ax2.plot(dates, temps, marker='o', linewidth=2)
    ax2.set_title('Temperature Trend (5 Days)')
    ax2.set_ylabel('Temperature (°C)')
    ax2.tick_params(axis='x', rotation=45)

# Panel 3: Today's Summary
today_data = get_today_summary()
if today_data and today_data[0]:
    min_temp, max_temp, readings = today_data
    ax3.bar(['Min', 'Max'], [min_temp, max_temp], color=['lightblue', 'lightcoral'])
    ax3.set_title(f"Today's Temperature ({readings} readings)")
    ax3.set_ylabel('Temperature (°C)')
    
    # Add padding above the highest bar
    max_value = max(min_temp, max_temp)
    padding = max_value * 0.15  # 15% padding above highest bar
    ax3.set_ylim(0, max_value + padding)
    
    # Position text labels with proper spacing
    for i, v in enumerate([min_temp, max_temp]):
        ax3.text(i, v + (padding * 0.3), f'{v:.1f}°C', ha='center', fontweight='bold')
    
    # Add explanation when min = max (if needed)
    if abs(min_temp - max_temp) < 0.01:
        ax3.text(0.5, min_temp - (padding * 0.6), f"Same value: Only {readings} reading(s) collected today", 
                ha='center', fontsize=9, style='italic', color='gray')

# Panel 4: Data Freshness
is_fresh = check_data_freshness()
if is_fresh:
    color = 'green'
    status = 'FRESH'
    symbol = '●'
else:
    color = 'red'
    status = 'STALE'
    symbol = '●'

ax4.text(0.5, 0.6, f"{symbol} Data Status:\n{status}", 
         ha='center', va='center', fontsize=12, fontweight='bold', color=color)
ax4.set_xlim(0, 1)
ax4.set_ylim(0, 1)
ax4.axis('off')

# Panel 5: Data Quality Report
quality_report = get_data_quality_report()
quality_text = f"""Data Quality Report:
Total Records: {quality_report['total_records']}
Missing Temp: {quality_report['missing_temp']}
Missing Humidity: {quality_report['missing_humidity']}
Outliers: {quality_report['outliers']}
Duplicates: {quality_report['duplicates']}"""

ax5.text(0.5, 0.5, quality_text, ha='center', va='center', fontsize=11, 
         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
ax5.set_title("Data Quality")
ax5.set_xlim(0, 1)
ax5.set_ylim(0, 1)
ax5.axis('off')

# Panel 6: Overall Quality Status
quality_report = get_data_quality_report()
total_issues = (quality_report['missing_temp'] + 
                quality_report['missing_humidity'] + 
                quality_report['outliers'] + 
                quality_report['duplicates'])

if total_issues == 0:
    symbol = '●'
    color = 'green'
    message = f"{symbol} PERFECT\nDATA QUALITY"
else:
    symbol = '●'
    color = 'orange'
    message = f"{symbol} {total_issues} ISSUES\nFOUND"

ax6.text(0.5, 0.6, message, 
         ha='center', va='center', fontsize=12, fontweight='bold', color=color)
ax6.set_xlim(0, 1)
ax6.set_ylim(0, 1)
ax6.axis('off')
ax6.set_title("Overall Quality")

plt.tight_layout()
plt.show()