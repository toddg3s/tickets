from datetime import date, datetime
from time import tzname
from dateutil import parser
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Any, Dict, List
import os


SCOPES = ["https://www.googleapis.com/auth/calendar"]

service_account_email = "tickets-service-account@tickets-g3s.iam.gserviceaccount.com"
credentials = service_account.Credentials.from_service_account_file("web/key.json")
scoped_credentials = credentials.with_scopes(SCOPES)

service = build("calendar", "v3", credentials=scoped_credentials)

class Event:
    id: str = ""
    calendarid: str = ""
    summary: str = ""
    name: str = ""
    location: str = ""
    start: datetime = datetime.min
    end: datetime = datetime.max
    status:str = ""
    interest: List[Dict[str, Any]] = []
    paid: bool = False
    transferred: bool = False

    def fromCalEvent(calevent, calendarid, calendarname) -> 'Event':
        event = Event()
        event.id = calevent['id']
        event.calendarid = calendarid
        event.summary = calevent['summary']
        event.name = calendarname
        event.location = calevent['location']
        event.start = parser.parse(calevent['start']['dateTime'])
        event.end = parser.parser(calevent['end']['dateTime'])
        event.status = 'unknown'
        if 'colorId' in calevent:
            if calevent['colorId'] == '0':
                event.status = 'available'
            elif calevent['colorid'] == '1':
                event.status = 'interest'
            elif calevent['colorid'] == '2':
                event.status = 'pending'
            elif calevent['colorid'] == '3':
                event.status = 'reserved'

        if 'extendedProperties' in calevent and 'private' in calevent['extendedProperties']:
            event.interest = calevent['extendedProperties']['private']['interest']
            event.paid = calevent['extendedProperties']['private']['paid']
            event.transferred = calevent['extendedProperties']['private']['transferred']
    

class Calendar:

    def ListEvents(calendarid: str, datefrom: date, dateto: date) -> List['Event']:
        calevents = service.events().list(calendarId=calendarid).execute()
        datetimeto = datetime(dateto.year, dateto.month, dateto.day, 23, 59, 59)

        events = [Event.fromCalEvent(e, calendarid, calevents['summary']) for e in calevents['items'] if e['start']['dateTime'] >= datefrom and e['start']['dateTime'] <= datetimeto]
        events.sort(key=lambda e: e.start, reverse=False)
        return events
    
    def GetEvent(eventid: str) -> 'Event':
        return None

    def UpdateEvent(event: 'Event'):
        pass