from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from package.scrape import run_scraper



# GMT == NYC time +4
def manage_scheduler(sched):
    today = datetime.today().date()
    start_time = datetime(today.year, today.month, today.day, 3, 31, 0)
    end_time = datetime(today.year, today.month, today.day, 6, 31, 0)
    # start_time = datetime(today.year, today.month, today.day, 14, 30, 0)
    # end_time = datetime(today.year, today.month, today.day, 14, 45, 0)

    print("Resetting run_scraper for today")
    sched.add_job(run_scraper, 'interval', minutes=15, start_date=start_time, end_date=end_time)
    # sched.add_job(run_scraper, 'interval', minutes=5, start_date=start_time, end_date=end_time)

def run_scheduler():
    sched = BackgroundScheduler(daemon=True)
    manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="3", minute="29", second="50")
    # manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="14", minute="29", second="50")
    sched.add_job(manage_scheduler, args=[sched], trigger=manage_jobs_trigger, start_date=datetime.now())
    print("Starting scheduler")
    sched.start()
