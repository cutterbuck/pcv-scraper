import http
import os
import urllib
from datetime import datetime
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def send_alert(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request(
        "POST",
        "/1/messages.json",
        urllib.parse.urlencode(
            {
                "token": os.environ.get("pushover_token"),
                "user": os.environ.get("pushover_user"),
                "message": message,
            }
        ),
        {"Content-type": "application/x-www-form-urlencoded"},
    )
    conn.getresponse()
    print("sent alert!")


def scrape_stuytown():
    print("Attempting a scrape...")
    url = "https://www.stuytown.com/nyc-apartments-for-rent?Order=low-price&PropertyName=Peter+Cooper+Village&Bedrooms=2&Flex=false&Bathrooms=2"

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-gpu")

    attempts = 0
    successes = 0
    while attempts < 10 and successes < 1:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//p[text()='2 Bed, 2 Bath']"))
            )
        except Exception:
            pass
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        first_div = soup.find("p", string="2 Bed, 2 Bath")
        if bool(first_div):
            successes += 1
        attempts += 1
        if attempts == 1 and successes == 1:
            print("First scrape success")
        elif attempts > 1 and successes == 1:
            print("Re-scrape success")
        else:
            print("Scrape attempt " + str(attempts) + " failed. Will try again.")
            driver.quit()

    driver.quit()
    return soup


def etl_data(soup):
    first_div = soup.find("p", string="2 Bed, 2 Bath").parent
    curr_classname = first_div["class"][0]
    mydivs = soup.find_all("div", {"class": curr_classname})
    scraped_listings = []

    if bool(mydivs):
        for div in mydivs:
            full_address = div.next.next.next.text.split(", Apt ")
            building = full_address[0]
            floor = full_address[-1].split("-")[0]
            unit = full_address[-1].split("-")[1]
            rent = int(div.span.text.split(" ")[-1].replace(",", "").replace("$", ""))
            available_by = div.p.next.next.next.next.next.replace("Available ", "")
            scraped_listings.append(
                {
                    "Building": building,
                    "Floor": floor,
                    "Unit": unit,
                    "Rent": rent,
                    "Date Available": available_by,
                }
            )
        return scraped_listings
    else:
        print("Check PCV URL --> div classname might have changed")
        send_alert("Check PCV URL --> div classname might have changed")
        return []


def run_scraper():
    soup = scrape_stuytown()
    listings = etl_data(soup)
    now = (
        datetime.now()
        .astimezone(ZoneInfo("America/New_York"))
        .strftime("%I:%M%p on %b %-d, %Y")
    )
    print(f"Scraped data at {now}")
    if not listings:
        return [], now
    cheap_filter = [apt for apt in listings if apt["Rent"] < 7000]
    if bool(cheap_filter):
        send_alert("Cheap PCV 2 bed/2 bath availability. Act fast!")
    return listings, now
