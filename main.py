from bs4 import BeautifulSoup

import pony.orm as pn
from libs.models import Event
import datetime

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def parse_date(input_date):
    if input_date:
        return datetime.datetime.strptime(input_date[:-5], "%Y-%m-%dT%H:%M:%S")
    else:
        return None

def get_ticketswap_id(link):
    return link[link.rfind('/') + 1:]

driver = webdriver.Firefox()

driver.get('https://www.ticketswap.com/city/amsterdam/3/anytime')

while True:
    try:
        WebDriverWait(driver, 10)
        load_more_button = driver.find_element_by_xpath('//div[@class="discover-load-more"]/a')
        load_more_button.click()
        break
    except Exception as e:
        print(e)
        break

soup = BeautifulSoup(driver.page_source, "lxml")
events = soup.find_all("div", class_="discover-result-item")

for event in events:
    with pn.db_session:
        node_link = event.find("a", {"itemprop": "url"})

        ticketswap_id = get_ticketswap_id(node_link["href"])
        node_start_date = event.find("meta", {"itemprop": "startDate"})

        if not Event.exists(ticketswap_id=ticketswap_id):
            start_date = None

            if node_start_date:
                start_date = parse_date(node_start_date["content"])

            node_end_date = event.find("meta", {"itemprop": "endDate"})
            end_date = None
            if node_end_date:
                end_date = parse_date(node_end_date["content"])

            event = Event(
                start_date=start_date,
                end_date=end_date,
                ticketswap_id = ticketswap_id,
                link=node_link["href"],
                title=node_link.get_text()
            )
            pn.flush()