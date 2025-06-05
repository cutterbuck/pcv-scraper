from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from package.dash_layout import update_trackers
from zoneinfo import ZoneInfo


def test_schedules():
    print("Hello world!")

def manage_scheduler(sched):
    print("Resetting scheduler for today")
    # update_trackers()
    today = datetime.today().date()
    start_time = datetime(today.year, today.month, today.day, 14, 25, 0).astimezone(ZoneInfo('America/New_York'))
    end_time = datetime(today.year, today.month, today.day, 14, 59, 0).astimezone(ZoneInfo('America/New_York'))
    sched.add_job(test_schedules, 'interval', minutes=5, start_date=start_time, end_date=end_time)

def run_scheduler():
    sched = BackgroundScheduler(daemon=True)
    manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="13", minute="20", second="0")
    sched.add_job(manage_scheduler, args=[sched], trigger=manage_jobs_trigger, start_date=datetime.now().astimezone(ZoneInfo('America/New_York')))
    sched.start()