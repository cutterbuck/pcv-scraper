import requests
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import csv, os, time


def run_scraper():
    url = 'PCV_SEARCH_URL'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        data = extract_data(soup)
        print(f"Scraped data at {datetime.now()}: {data}")
        process_data(data)
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_data(soup):
    # implement data extraction from soup logic here
    import pdb; pdb.set_trace()
    all_apts = soup.final_all('a', href=True)
    below_mkt_apts = []
    for apt in all_apts:
        if apt['price'] < 7000:
            below_mkt_apts.append(apt)
    return below_mkt_apts

def update_csv_file(below_mkt_apts):
    with open(os.getcwd()+'/cheap_listings.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_row_dict.keys())
        for apt in below_mkt_apts:
            new_row = dict(date, rent, finish, address, floor)
            writer.writerow(new_row)

def process_data(below_mkt_apts):
    if bool(below_mkt_apts):
        update_csv_file(below_mkt_apts)
        send_alert()

def send_alert():
    print("New below market 2bed2bath listings")

def manage_scheduler(sched):
    today = datetime.today().date()
    start_time = datetime(today.year, today.month, today.day, 4, 0, 0)
    end_time = datetime(today.year, today.month, today.day, 7, 0, 0)
    sched.add_job(run_scraper, 'interval', minutes=15, start_date=start_time, end_date=end_time)

def run_scheduler():
    sched = BackgroundScheduler(daemon=True)
    manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="22", minute="00", second="50")
    sched.add_job(manage_scheduler, args=[sched], trigger=manage_jobs_trigger, start_date=datetime.now())
    sched.start()


if __name__ == "__main__":
    print("Running app")
    run_scheduler()

    while True:
        time.sleep(1)
