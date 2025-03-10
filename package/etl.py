from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from package.models import Listing, db


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
        data = etl_data(soup)
        print(f"Scraped data at {datetime.now()}: {data}")
        if bool(data):
            send_alert()
    except Exception as e:
        print(f"An error occurred: {e}")

def etl_data(soup):
    mydivs = soup.find_all('div', {"class": "bK_kp"})
    new_listings = []
    for div in mydivs:
        full_address = div.next.next.next.text.split(', Apt ')
        building = full_address[0]
        floor = full_address[-1].split('-')[0]
        unit = full_address[-1].split('-')[1]
        rent = int(div.span.text.split(" ")[-1].replace(',', '').replace('$', ''))
        status = 'available'
        if rent < 7400:
            existing_listing = Listing.query.filter(Listing.posting_date==datetime.now().date(), Listing.building==building, Listing.floor==floor, Listing.unit==unit, Listing.rent==rent).first()
            if bool(existing_listing) == False:
                new_listing = Listing(posting_date=datetime.now().date(), building=building, floor=floor, unit=unit, rent=rent, status=status)
                db.session.add(new_listing)
                new_listings.append(new_listing)
            db.session.commit()
    return new_listings

def send_alert():
    print("New below market 2bed2bath listings available")

def manage_scheduler(sched):
    today = datetime.today().date()
    start_time = datetime(today.year, today.month, today.day, 4, 0, 0)
    end_time = datetime(today.year, today.month, today.day, 7, 0, 0)
    print("Resetting run_scraper for today")
    sched.add_job(run_scraper, 'interval', minutes=20, start_date=start_time, end_date=end_time)

def run_scheduler():
    sched = BackgroundScheduler(daemon=True)
    manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="3", minute="59", second="50")
    sched.add_job(manage_scheduler, args=[sched], trigger=manage_jobs_trigger, start_date=datetime.now())
    print("Starting scheduler")
    sched.start()
