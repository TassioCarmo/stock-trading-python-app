import schedule
import time
from script import run_stock_job

from datetime import datetime

"""Scheduler to run stock job at specified intervals."""
def basic_job():
    print("Job started at:", datetime.now())

# Run every minute
schedule.every().minute.do(basic_job)

# Run every day at 10:30 AM
# schedule.every().day.at("10:30").do(run_stock_job)

# Run every minute
schedule.every().minute.do(run_stock_job)

while True:
    schedule.run_pending()
    time.sleep(1)
    
    
## problem with sheduler like this is that if you close your laptop the scheduler stops working