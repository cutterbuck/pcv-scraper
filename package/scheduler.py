from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
# from package.dash_layout import update_trackers
from zoneinfo import ZoneInfo


def test_schedules():
    print("Hello world!")

def manage_scheduler(sched):
    print("Resetting scheduler jobs")
    # update_trackers()
    today = datetime.today().date()
    start_time = datetime(today.year, today.month, today.day, 19, 25, 0).astimezone(ZoneInfo('UTC'))
    end_time = datetime(today.year, today.month, today.day, 20, 59, 0).astimezone(ZoneInfo('UTC'))
    sched.add_job(test_schedules, 'interval', minutes=5, start_date=start_time, end_date=end_time)

def run_scheduler():
    print("Starting scheduler")
    sched = BackgroundScheduler(daemon=True)
    manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="19", minute="20", second="0")
    sched.add_job(manage_scheduler, args=[sched], trigger=manage_jobs_trigger, start_date=datetime.now().astimezone(ZoneInfo('UTC')))
    sched.start()