from bs4 import BeautifulSoup

import pony.orm as pn
from libs.models import Event, SubEvent, Client, TicketOffer
import datetime
import requests


class TicketParser:

    def __init__(self, event_id):
        with pn.db_session:
            self.event = Event.get(id=event_id)

    def parse(self):
        with requests.get(utils.DOMAIN_NAME + self.event.link) as r:
            soup = BeautifulSoup(r.text, "lxml")


        tickets = soup.find_all("article", {"itemprop": "tickets"})
