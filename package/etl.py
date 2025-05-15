from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from package.models import Listing, db
from package.app import app
import http, urllib, os, shutil



def send_alert(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": os.environ.get('pushover_token'),
            "user": os.environ.get('pushover_user'),
            "message": message,
        }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    print("sent alert!")
# send_alert("hello jake")

def scrape_stuytown():
    print("Hello world!!! Attempting to scrape")
    url = 'https://www.stuytown.com/nyc-apartments-for-rent?Order=low-price&PropertyName=Peter+Cooper+Village&Bedrooms=2&Flex=false&Bathrooms=2'

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-gpu")
    driver = webdriver.Chrome(service=service, options=options)
    print("made it past driver")
    driver.get(url)
    html = driver.page_source
    print('received html')
    soup = BeautifulSoup(html, "lxml")
    driver.quit()
    return soup

def etl_data(soup):
    first_div = soup.find('p', string="2 Bed, 2 Bath").parent
    curr_classname = first_div['class'][0]
    mydivs = soup.find_all('div', {"class": curr_classname})
    scraped_listings = []
    now = datetime.now()

    if bool(mydivs):
        with app.server.app_context():
            for div in mydivs:
                full_address = div.next.next.next.text.split(', Apt ')
                building = full_address[0]
                floor = full_address[-1].split('-')[0]
                unit = full_address[-1].split('-')[1]
                rent = int(div.span.text.split(" ")[-1].replace(',', '').replace('$', ''))
                existing_listing = Listing.query.filter(Listing.building==building, Listing.floor==floor, Listing.unit==unit, Listing.status=='available').first()

                if bool(existing_listing):
                    existing_listing.days_listed=(now.date() - existing_listing.initial_posting_date).days + 1
                    if rent != existing_listing.current_rent:
                        existing_listing.last_updated=now.date()
                        existing_listing.update_time=now.strftime('%-I:%M:%S%p')
                        existing_listing.current_rent=rent
                        existing_listing.rent_change=rent - existing_listing.initial_rent
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
                    existing_listing.last_updated=now.date()
                    existing_listing.update_time=now.strftime('%-I:%M:%S%p')
                    db.session.add(listing)
            db.session.commit()

    else:
        send_alert("Check PCV URL --> div classname might have changed")

def run_scraper():
    soup = scrape_stuytown()
    etl_data(soup)
    print(f"Scraped data at {datetime.now()}")
    listings = Listing.query.filter(Listing.status == 'available').all()
    cheap_filter = [el for el in listings if el.current_rent < 7000]
    if bool(cheap_filter): send_alert("Cheap 2PCV bed/2bath availability. Act fast!")


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
    # run_scraper()
    sched.start()
