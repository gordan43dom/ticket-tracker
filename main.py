from bs4 import BeautifulSoup

import pony.orm as pn
from libs.models import Event, SubEvent
import datetime
import requests

import libs.utils as utils
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait




class EventParser:

    def __init__(self, start_point):
        self.driver = webdriver.Firefox()
        self.driver.get(start_point)

    @classmethod
    def get_ticketswap_id(self, link):
        return link[link.rfind('/') + 1:]

    @classmethod
    def parse_date(self, input_date):

        if input_date:
            return datetime.datetime.strptime(input_date[:-5], "%Y-%m-%dT%H:%M:%S")
        else:
            return None

    def parse(self):

        while True:
            try:
                WebDriverWait(self.driver, 10)
                load_more_button = self.driver.find_element_by_xpath('//div[@class="discover-load-more"]/a')
                load_more_button.click()
            except Exception as e:
                print(e)
                break

        soup = BeautifulSoup(self.driver.page_source, "lxml")
        events = soup.find_all("div", class_="discover-result-item")

        for event in events:
            with pn.db_session:
                node_link = event.find("a", {"itemprop": "url"})
                ticketswap_id = EventParser.get_ticketswap_id(node_link["href"])

                if not event.exists(ticketswap_id=ticketswap_id):
                    start_date = None

                    node_start_date = event.find("meta", {"itemprop": "startDate"})
                    if node_start_date:
                        start_date = EventParser.parse_date(node_start_date["content"])

                    node_end_date = event.find("meta", {"itemprop": "endDate"})
                    end_date = None
                    if node_end_date:
                        end_date = EventParser.parse_date(node_end_date["content"])

                    if node_link["href"]:
                        locObj = LocationParser(node_link["href"])
                        location = locObj.parse()


                    try:
                        event = Event(
                            start_date=start_date,
                            end_date=end_date,
                            ticketswap_id=ticketswap_id,
                            link=node_link["href"],
                            title=node_link.get_text(),
                            location=location,
                            created_at= datetime.datetime.now()
                        )
                        pn.commit()
                    except Exception as e:
                        print(e)



class SubEventParser:

    def __init__(self, parent_id):
        with pn.db_session:
            self.parent = Event.get(id=parent_id)

    @classmethod
    def parse_date(self, input_date):

        if input_date:
            return datetime.datetime.strptime(input_date[:-1], "%Y-%m-%dT%H:%M:%S")
        else:
            return None

    def parse(self):

        with requests.get(utils.DOMAIN_NAME + self.parent.link) as r:
            soup = BeautifulSoup(r.text, "lxml")

        subevents= soup.find_all("article", {"itemprop": "subEvent"})

        if(subevents):
            for subevent in subevents:
                with pn.db_session:
                    node_link = subevent.find("a", {"itemprop": "url"})
                    ticketswap_id = EventParser.get_ticketswap_id(node_link["href"])

                    if not SubEvent.exists(ticketswap_id=ticketswap_id):

                        start_date = None

                        node_start_date = subevent.find("meta", {"itemprop": "startDate"})
                        if node_start_date:
                            start_date = SubEventParser.parse_date(node_start_date["content"])

                        node_end_date = subevent.find("meta", {"itemprop": "endDate"})
                        end_date = None

                        if node_end_date:
                            end_date = SubEventParser.parse_date(node_end_date["content"])

                        if node_link["href"]:
                            locObj = LocationParser(node_link["href"])
                            location = locObj.parse()

                        try:
                            print(node_link.get_text())
                            subevent = SubEvent(
                                start_date=start_date,
                                end_date=end_date,
                                ticketswap_id=ticketswap_id,
                                link=node_link["href"],
                                title=node_link.get_text(),
                                parent_id=self.parent.id,
                                created_at=datetime.datetime.now(),
                                location=location
                            )
                            pn.commit()
                            print(subevent)
                        except Exception as e:
                            print(e)


class LocationParser:

    def __init__(self, event_link):
        with pn.db_session:
            self.event_link = event_link


    def parse(self):

        with requests.get(utils.DOMAIN_NAME + self.event_link) as r:
            soup = BeautifulSoup(r.text, "lxml")

        location = soup.findAll("span", {"itemprop": "location"})

        return location[0].text




parser = EventParser("https://www.ticketswap.com/city/amsterdam/3/anytime")
parser.parse()

with pn.db_session:
    events = Event.select(lambda e: e.parent_id is None)
    for e in events:
        subEventParser = SubEventParser(e.id)
        subEventParser.parse()

