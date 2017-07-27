import pony.orm as pn
import datetime

db = pn.Database()


class Event(db.Entity):
    link = pn.Required(pn.unicode, unique=True)
    title = pn.Required(pn.unicode)
    ticketswap_id = pn.Optional(pn.unicode)
    location = pn.Optional(pn.unicode)
    start_date = pn.Required(datetime.datetime)
    end_date = pn.Optional(datetime.datetime)
    created_at = pn.Required(datetime.datetime)

    tickets = pn.Set("TicketOffer", cascade_delete=True)
    subevents = pn.Set("SubEvent", cascade_delete=True)


class SubEvent(Event):
    parent_id = pn.Required(Event)


class Client(db.Entity):
    name = pn.Required(pn.unicode, unique=True)
    link = pn.Required(pn.unicode, unique=True)
    facebook_id = pn.Required(pn.unicode)
    created_at = pn.Required(datetime.datetime)
    sold_tickets = pn.Set("TicketOffer")


class TicketOffer(db.Entity):
    number_of_tickets = pn.Required(int)
    link = pn.Required(pn.unicode, unique=True)
    ticketswap_id = pn.Required(pn.unicode, unique=True)
    original_price = pn.Optional(str)
    selling_price = pn.Required(str)
    sold_date = pn.Optional(datetime.datetime)
    showup_date = pn.Optional(datetime.datetime)
    created_at = pn.Required(datetime.datetime)
    status = pn.Required(str)
    event = pn.Required(Event)
    salesman = pn.Required(Client)

db.bind(provider='mysql', host='localhost', db='ticketswap', user='root', passwd='root')
db.generate_mapping(create_tables=True)