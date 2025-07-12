import schedule
import time
from etl import run as etl_run  # Import your existing ETL function
from datetime import datetime

# This is the function we want to run automatically
def scheduled_weather_job():
    """
    This wrapper function adds logging to your ETL process
    """
    print(f"🕒 [{datetime.now()}] Starting scheduled weather collection...")
    
    # Call your existing ETL function
    etl_run()
    
    print(f"✅ [{datetime.now()}] Weather data collection completed!")
    print("-" * 50)

# SCHEDULING SETUP - This is where the magic happens!
print("⚡ Setting up weather data collection schedule...")

# DEMO VERSION: Every 2 minutes for testing (instead of 30 minutes)
schedule.every(2).minutes.do(scheduled_weather_job)
print("📅 Scheduled: Every 2 minutes (DEMO MODE)")

# Alternative schedules (commented out for now):
# schedule.every(30).minutes.do(scheduled_weather_job)  # Production version
# schedule.every(2).hours.do(scheduled_weather_job)
# schedule.every().day.at("09:00").do(scheduled_weather_job)
# schedule.every().monday.at("10:00").do(scheduled_weather_job)

print("🚀 Starting scheduler... Press Ctrl+C to stop")
print("⏰ (This demo will run for 5 minutes, then stop automatically)")
print("=" * 50)

# THE SCHEDULING LOOP - This keeps checking "is it time to run?"

# DEMO TIME LIMIT SETUP
start_time = datetime.now()          # Remember when we started
max_runtime_minutes = 5              # Stop after 5 minutes for demo
# WHY: Without this, the loop runs forever. For learning, we want it to stop.

# TRY/EXCEPT BLOCK - Handle user interruptions gracefully
try:
    # TRY means: "Try to do this code, but be ready for problems"
    
    while True:  # This is the infinite loop you learned about!
        # THE HEART: Check if any scheduled jobs are ready to run
        schedule.run_pending()
        # This is exactly like your mini-scheduler example!
        
        # DEMO TIME CHECK (you can ignore this part in production)
        runtime = (datetime.now() - start_time).total_seconds() / 60
        # Calculate: How many minutes have passed since we started?
        
        if runtime > max_runtime_minutes:
            # If more than 5 minutes passed, stop the demo
            print(f"\n⏰ Demo time limit reached ({max_runtime_minutes} minutes)")
            print("🛑 Stopping scheduler...")
            break  # Exit the while loop
            # WHY: Without this, you'd have to wait forever to see results
        
        # Wait 1 second before checking again (prevents CPU overload)
        time.sleep(1)
        # This is exactly like your learning examples!
        
except KeyboardInterrupt:
    # EXCEPT means: "If something goes wrong, do this instead"
    # KeyboardInterrupt = when user presses Ctrl+C
    print("\n🛑 Scheduler stopped by user")
    # WHY: Without this, pressing Ctrl+C shows ugly error messages

# This line runs no matter how the loop ended (time limit or Ctrl+C)
print("👋 Scheduler demo complete!")
print(f"💾 Check your output/ folder for new weather data!") 