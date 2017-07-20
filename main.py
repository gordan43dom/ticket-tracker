from bs4 import BeautifulSoup

import pony.orm as pn
from libs.models import Event
import datetime
import urllib

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

DOMAIN_NAME="https://ticketswap.nl"

def parse_date(input_date):
    if input_date:
        return datetime.datetime.strptime(input_date[:-5], "%Y-%m-%dT%H:%M:%S")
    else:
        return None


class EventParser:

    def __init__(self, start_point):
        self.driver = webdriver.Firefox()
        self.driver.get(start_point)

    @classmethod
    def get_ticketswap_id(self, link):
        return link[link.rfind('/') + 1:]

    def parse(self):

        while True:
            try:
                WebDriverWait(self.driver, 10)
                load_more_button = self.driver.find_element_by_xpath('//div[@class="discover-load-more"]/a')
                load_more_button.click()
                break
            except Exception as e:
                print(e)
                break

        soup = BeautifulSoup(self.driver.page_source, "lxml")
        events = soup.find_all("div", class_="discover-result-item")

        for event in events:
            with pn.db_session:
                node_link = event.find("a", {"itemprop": "url"})

                ticketswap_id = EventParser.get_ticketswap_id(node_link["href"])
                #description=event.find("p", {"class": "discover-result-item--description"})

                if not Event.exists(ticketswap_id=ticketswap_id):
                    start_date = None

                    node_start_date = event.find("meta", {"itemprop": "startDate"})
                    if node_start_date:
                        start_date = parse_date(node_start_date["content"])

                    node_end_date = event.find("meta", {"itemprop": "endDate"})
                    end_date = None
                    if node_end_date:
                        end_date = parse_date(node_end_date["content"])

                    event = Event(
                        start_date=start_date,
                        end_date=end_date,
                        ticketswap_id=ticketswap_id,
                        link=node_link["href"],
                        title=node_link.get_text(),
                        #location = description[1].get_text()
                    )
                    pn.flush()

class SubEventParser:

    def __init__(self, parent_id):
        with pn.db_session:
            self.parent = Event.get(id=parent_id)

    def parse(self):
        urllib.
        with urllib.urlopen(DOMAIN_NAME + self.parent.link).read()as r:
            soup = BeautifulSoup(r)

        print(soup)


#parser = EventParser("https://www.ticketswap.com/city/amsterdam/3/anytime")
#parser.parse()

subEventParser = SubEventParser(1)
subEventParser.parse()

