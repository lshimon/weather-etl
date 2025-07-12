import schedule
import time
from datetime import datetime

def my_job():
    print(f"✅ JOB EXECUTED at {datetime.now()}")

# Schedule the job
schedule.every(10).seconds.do(my_job)

print("📋 Scheduled jobs:", schedule.jobs)
print("⏰ Starting loop...")

# THE LOOP - Let's see what happens step by step
for i in range(30):  # Run for 30 seconds instead of forever
    print(f"\n🔍 Loop iteration {i+1}")
    print(f"⏰ Current time: {datetime.now()}")
    
    # Check if any jobs are ready
    pending_jobs = [job for job in schedule.jobs if job.should_run]
    print(f"📋 Jobs ready to run: {len(pending_jobs)}")
    
    if pending_jobs:
        print("🚀 EXECUTING JOBS NOW!")
    
    # THIS IS THE LINE THAT ACTUALLY RUNS YOUR FUNCTION!
    schedule.run_pending()
    
    time.sleep(1)

print("\n🏁 Loop finished") 