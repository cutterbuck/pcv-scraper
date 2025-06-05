from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from package.dash_layout import update_trackers
from zoneinfo import ZoneInfo



# GMT == NYC time +4
def manage_scheduler(sched):
    print("Resetting scheduler for today")
    update_trackers()
    today = datetime.today().date()
    start_time = datetime(today.year, today.month, today.day, 12, 25, 0).astimezone(ZoneInfo('America/New_York'))
    end_time = datetime(today.year, today.month, today.day, 12, 59, 0).astimezone(ZoneInfo('America/New_York'))
    sched.add_job(update_trackers, 'interval', minutes=5, start_date=start_time, end_date=end_time)

def run_scheduler():
    sched = BackgroundScheduler(daemon=True)
    # manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="3", minute="29", second="50")
    manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="12", minute="19", second="50")
    sched.add_job(manage_scheduler, args=[sched], trigger=manage_jobs_trigger, start_date=datetime.now().astimezone(ZoneInfo('America/New_York')))
    sched.start()