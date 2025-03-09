import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import csv, os, time


def run_scraper():
    url = 'https://www.stuytown.com/nyc-apartments-for-rent?Order=low-price&PropertyName=Peter+Cooper+Village&Bedrooms=2&Flex=false&Bathrooms=2'
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless') # ensure GUI is off
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        driver.close()
        data = extract_data(soup)
        print(f"Scraped data at {datetime.now()}: {data}")
        process_data(data)
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_data(soup):
    mydivs = soup.find_all('div', {"class": "bK_kp"})
    below_mkt_apts = []
    for div in mydivs:
        full_address = div.next.next.next.text.split(', Apt ')
        building = full_address[0]
        floor = full_address[-1].split('-')[0]
        unit = full_address[-1].split('-')[1]
        rent = int(div.span.text.split(" ")[-1].replace(',', '').replace('$', ''))
        if rent < 7400:
            below_mkt_apts.append(dict(posting_date=datetime.now().date().strftime('%-m/%-d/%y'), building=building, floor=floor, unit=unit, rent=rent))
    return below_mkt_apts

def update_csv_file(below_mkt_apts):
    with open(os.getcwd()+'/cheap_listings.csv', 'a', newline='') as f:
        for apt in below_mkt_apts:
            writer = csv.DictWriter(f, fieldnames=apt.keys(), quoting=csv.QUOTE_NONE)
            writer.writerow(apt)

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
    manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="3", minute="59", second="50")
    sched.add_job(manage_scheduler, args=[sched], trigger=manage_jobs_trigger, start_date=datetime.now())
    sched.start()


if __name__ == "__main__":
    run_scraper()

    # run_scheduler()
    # while True:
    #     time.sleep(1)
