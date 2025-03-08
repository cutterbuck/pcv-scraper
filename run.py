import requests
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


def scrape_website():
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

def process_data(below_mkt_apts):
    # write to csv file here
    import pdb; pdb.set_trace()
    if bool(below_mkt_apts):
        # with open("scraped_data.csv", "a") as file:
            # file.write()
        send_alert()

def send_alert():
    # send alert to my cell phone here
    print("Text alert to cell phone")
    # import pdb; pdb.set_trace()

def run_scraper():
    scrape_website()

def run_scheduler():
    today = datetime.today().date()
    sched.add_job(run_scraper, 'interval', minutes=15, start_date=today.first_update_time(), end_date=today.crunch_time_update_start())

if __name__ == "__main__":
    while True:
        run_scheduler()