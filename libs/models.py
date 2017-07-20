import pony.orm as pn
import datetime

db = pn.Database()


class Event(db.Entity):

    link = pn.Required(pn.unicode, unique=True)
    title = pn.Required(pn.unicode)
    ticketswap_id = pn.Optional(pn.unicode)
    location = pn.Optional(pn.unicode)
    start_date = pn.Required(datetime.date)
    end_date = pn.Optional(datetime.date)

    subevents = pn.Set("SubEvent", cascade_delete=True)


class SubEvent(Event):
    parent_id = pn.Required(Event)


db.bind(provider='mysql', host='localhost', db='ticketswap', user='root', passwd='root')
db.generate_mapping(create_tables=True)