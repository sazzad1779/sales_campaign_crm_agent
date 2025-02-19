from apscheduler.schedulers.background import BackgroundScheduler
from supervisor import run_supervisor_workflow
import time



# Initialize the scheduler
scheduler = BackgroundScheduler()

# Schedule the workflow to run every day at 9 AM
# scheduler.add_job(run_supervisor_workflow, 'cron', hour=9, minute=0)
time_=1
scheduler.add_job(run_supervisor_workflow, 'interval', minutes=time_)

# Start the scheduler
scheduler.start()

print(f"⏳ APScheduler started. Sales campaign automation will run after {time_} minutes.")

# Keep the script running
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler stopped.")
