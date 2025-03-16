from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from package.models import Listing, db
from package.app import app
import http, urllib
import os


def run_scraper():
    url = 'https://www.stuytown.com/nyc-apartments-for-rent?Order=low-price&PropertyName=Peter+Cooper+Village&Bedrooms=2&Flex=false&Bathrooms=2'
    try:
        s=Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') # ensure GUI is off
        options.add_argument("--no-sandbox")
        options.headless = True
        driver = webdriver.Chrome(service=s, options=options)
        driver.get(url)
        html = driver.page_source
        print('received html')
        soup = BeautifulSoup(html, "lxml")
        driver.close()
        data = etl_data(soup)
        print(f"Scraped data at {datetime.now()}: {data}")
        send_alert(data)
    except Exception as e:
        print(f"An error occurred: {e}")

def etl_data(soup):
    mydivs = soup.find_all('div', {"class": "bK_kp"})
    scraped_listings = []
    now = datetime.now()

    with app.server.app_context():
        for div in mydivs:
            full_address = div.next.next.next.text.split(', Apt ')
            building = full_address[0]
            floor = full_address[-1].split('-')[0]
            unit = full_address[-1].split('-')[1]
            rent = int(div.span.text.split(" ")[-1].replace(',', '').replace('$', ''))
            existing_listing = Listing.query.filter(Listing.building==building, Listing.floor==floor, Listing.unit==unit, Listing.status=='available').first()
            if bool(existing_listing):
                if existing_listing.last_updated != now.date():
                    existing_listing.last_updated=now.date()
                    existing_listing.update_time=now.strftime('%-I:%M:%S%p')
                    existing_listing.current_rent=rent
                    existing_listing.rent_change=rent - existing_listing.initial_rent
                    existing_listing.days_listed=(now.date() - existing_listing.initial_posting_date).days + 1
                    db.session.add(existing_listing)
                scraped_listings.append(existing_listing)
            else:
                new_listing = Listing(initial_posting_date=now.date(), last_updated=now.date(), update_time=now.strftime('%-I:%M:%S%p'), building=building, floor=floor, unit=unit, initial_rent=rent, rent_change=0, current_rent=rent, days_listed=1, status='available')
                db.session.add(new_listing)
                scraped_listings.append(new_listing)
            db.session.commit()

        all_available_listings = Listing.query.filter(Listing.status=='available').all()
        for listing in all_available_listings:
            if listing not in scraped_listings:
                listing.status = 'unavailable'
                db.session.add(listing)

    return scraped_listings

def send_alert(new_listings):
    cheap_filter = [el for el in new_listings if el.current_rent < 7500]
    if bool(cheap_filter):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": os.environ.get('pushover_token'),
                "user": os.environ.get('pushover_user'),
                "message": "Cheap 2PCV bed/2bath availability. Act fast!",
            }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        print("sent alert!")

run_scraper()
# GMT == NYC time +4
def manage_scheduler(sched):
    today = datetime.today().date()
    start_time = datetime(today.year, today.month, today.day, 18, 25, 0)
    end_time = datetime(today.year, today.month, today.day, 19, 10, 0)
    print("Resetting run_scraper for today")
    sched.add_job(run_scraper, 'interval', minutes=15, start_date=start_time, end_date=end_time)

def run_scheduler():
    sched = BackgroundScheduler(daemon=True)
    manage_jobs_trigger = CronTrigger(year="*", month="*", day="*", hour="18", minute="20", second="50")
    sched.add_job(manage_scheduler, args=[sched], trigger=manage_jobs_trigger, start_date=datetime.now())
    print("Starting scheduler")
    sched.start()
