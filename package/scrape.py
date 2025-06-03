from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
# from package.app import app
import http, urllib, os



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
    import pdb; pdb.set_trace()
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
    print("inside run_scraper")
    soup = scrape_stuytown()
    etl_data(soup)
    print(f"Scraped data at {datetime.now()}")
    listings = Listing.query.filter(Listing.status == 'available').all()
    cheap_filter = [el for el in listings if el.current_rent < 7000]
    if bool(cheap_filter): send_alert("Cheap 2PCV bed/2bath availability. Act fast!")
