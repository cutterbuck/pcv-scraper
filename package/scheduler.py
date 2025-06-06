from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from package.dash_layout import update_trackers
from zoneinfo import ZoneInfo



def manage_scheduler(sched):
    print("Resetting scheduler jobs")
    today = datetime.today().date()
    # start_time = datetime(today.year, today.month, today.day, 7, 0, 0).astimezone(ZoneInfo('UTC'))
    # end_time = datetime(today.year, today.month, today.day, 10, 0, 0).astimezone(ZoneInfo('UTC'))
    start_time = datetime(today.year, today.month, today.day, 14, 15, 0).astimezone(ZoneInfo('UTC'))
    end_time = datetime(today.year, today.month, today.day, 16, 0, 0).astimezone(ZoneInfo('UTC'))
    sched.add_job(update_trackers, 'interval', minutes=15, start_date=start_time, end_date=end_time)

def run_scheduler():
    print("Starting scheduler")
    update_trackers()
    sched = BackgroundScheduler(daemon=True)
    # manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="6", minute="59", second="0")
    manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="14", minute="10", second="0")
    sched.add_job(manage_scheduler, args=[sched], trigger=manage_jobs_trigger, start_date=datetime.now().astimezone(ZoneInfo('UTC')))
    sched.start()