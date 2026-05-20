import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from package.dash_layout import update_trackers
from zoneinfo import ZoneInfo



def run_scheduler():
    print("Starting scheduler")

    sched = BackgroundScheduler(daemon=True)
    trigger = CronTrigger(
        year="*",
        month="*",
        day="*",
        hour="7-10",
        minute="0,15,30,45",
        second="0",
        end_date=datetime(2026, 12, 31, 17, 0, 0).astimezone(ZoneInfo('UTC')),
        timezone=ZoneInfo('UTC')
    )
    sched.add_job(update_trackers, trigger=trigger, kwargs={"alert": True})
    sched.add_job(update_trackers, id="startup_scrape")
    sched.start()
