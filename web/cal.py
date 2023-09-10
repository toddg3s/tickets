from datetime import date, datetime
from time import tzname
from dateutil import parser
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Any, Dict, List

import pytz
import json


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
    interest = []
    paid: bool = False
    transferred: bool = False

    def fromCalEventOld(calevent, calendarid, calendarname) -> 'Event':
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
            elif calevent['colorId'] == '1':
                event.status = 'interest'
            elif calevent['colorId'] == '2':
                event.status = 'pending'
            elif calevent['colorId'] == '3':
                event.status = 'reserved'

        if 'extendedProperties' in calevent and 'private' in calevent['extendedProperties']:
            event.interest = calevent['extendedProperties']['private']['interest']
            event.paid = calevent['extendedProperties']['private']['paid']
            event.transferred = calevent['extendedProperties']['private']['transferred']

        return event

    def fromCalEvent(calevent, calendarid, calendarname):
        event = {
            "id": calevent["id"],
            "calendarid": calendarid,
            "summary": calevent["summary"],
            "name": calendarname,
            "location": calevent["location"],
            "start": parser.parse(calevent["start"]["dateTime"]),
            "end": parser.parse(calevent["end"]["dateTime"]),
            "startts": calevent["start"]["dateTime"],
            "endts": calevent["end"]["dateTime"],
            "status": "unknown",
            "attendee": "",
            "interest": "",
            "paid": False,
            "transferred": False,
        }
        if 'colorId' in calevent:
            if calevent['colorId'] == '2': # green
                event["status"] = 'available'
            elif calevent['colorId'] == '5': # yellow
                event["status"] = 'interest'
            elif calevent['colorId'] == '7': # blue
                event["status"] = 'pending'
            elif calevent['colorId'] == '11': # red
                event["status"] = 'reserved'

        if 'extendedProperties' in calevent and 'private' in calevent['extendedProperties']:
            if "attendee" in calevent["extendedProperties"]["private"]:
                event["attendee"] = calevent["extendedProperties"]["private"]["attendee"]
            if "interest" in calevent["extendedProperties"]["private"]:
                event["interest"] = calevent['extendedProperties']['private']['interest']
            event["paid"] = False
            if "paid" in calevent["extendedProperties"]["private"]:     
                event["paid"] = calevent['extendedProperties']['private']['paid']
            event["transferred"] = False
            if "transferred" in calevent["extendedProperties"]["private"]:
                event["transferred"] = calevent['extendedProperties']['private']['transferred']

        return event


class Calendar:

    def ListEvents(calendarid: str, calendarname: str, datefrom: date, dateto: date) -> List['Event']:
        calevents = service.events().list(calendarId=calendarid).execute()
        datetimefrom = datetime(datefrom.year, datefrom.month, datefrom.day, 0, 0, 0)
        datetimeto = datetime(dateto.year, dateto.month, dateto.day, 23, 59, 59)
        leftcoast = pytz.timezone('US/Pacific')
        events = [Event.fromCalEvent(e, calendarid, calendarname) for e in calevents['items'] if parser.parse(e['start']['dateTime']) >= leftcoast.localize(datetimefrom) and parser.parse(e['start']['dateTime']) <= leftcoast.localize(datetimeto)]
        events.sort(key=lambda e: e["start"], reverse=False)
        return events
    
    def GetEvent(calendarid: str, eventid: str):
        calevent = service.events().get(calendarId=calendarid, eventId=eventid).execute()
        return Event.fromCalEvent(calevent, calendarid, "")

    def UpdateEvent(event):
        calevent = service.events().get(calendarId=event["calendarid"], eventId=event["id"]).execute()
        if event["status"] == "available":
            calevent["colorId"] = "2"
        elif event["status"] == "interest":
            calevent["colorId"] = "5"
        elif event["status"] == "pending":
            calevent["colorId"] = "7"
        else:
            calevent["colorId"] = "11"
        props = {
            "attendee": "",
            "interest": [],
            "paid": False,
            "transferred": False
        }
        if "attendee" in event and event["attendee"] != "":
            props["attendee"] = event["attendee"]
        if "paid" in event:
            props["paid"] = event["paid"]
        if "transferred" in event:
            props["transferred"] = event["transferred"]
        if "interest" in event:
            props["interest"] = event["interest"]
        calevent["extendedProperties"] = {
            "private": props
        }
        service.events().update(calendarId = event["calendarid"], eventId=event["id"], body=calevent).execute()
