from datetime import date, datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
from typing import List
import re
from django.db import models
from web.models import NHLStats, Ticket, TicketSet
from web.cal import Event, Calendar
import json
class DateRange:
    datefrom = date.min
    dateto = date.max
    type = None

    def __init__(self, datefrom : date, type):
        self.type = type
        if type == "year":
            self.datefrom = date(datefrom.year, 1, 1)
            self.dateto = date(datefrom.year, 12, 31)
        elif type == "month":
            self.datefrom = date(datefrom.year, datefrom.month, 1)
            self.dateto = DateRange.lastday(datefrom, type)
        elif type == "week":
            self.datefrom = datefrom - relativedelta(days=datefrom.weekday())
            self.dateto = self.datefrom + relativedelta(days=6)
        elif type == "list":
            self.datefrom = datefrom
            self.dateto = date.max
        else:
            self.datefrom = datefrom
            self.dateto = datefrom
        
    def previous(self):
        if self.type == "year":
            return str(self.datefrom.year - 1)
        elif self.type == "month":
            prev = self.datefrom - relativedelta(months = 1)
            return prev.strftime("%m-%Y")
        elif self.type == "week":
            prev = self.datefrom - relativedelta(days = 7)
            return prev.strftime("%Y-%m-%d")
        else:
            return ""

    def next(self):
        if self.type == "year":
            return str(self.datefrom.year + 1)
        elif self.type == "month":
            next = self.datefrom + relativedelta(months = 1)
            return next.strftime("%m-%Y")
        elif self.type == "week":
            next = self.datefrom + relativedelta(days = 7)
            return next.strftime("%Y-%m-%d")
        else:
            return ""


    def __str__(self):
        if self.type is None:
            if self.datefrom == self.dateto:
                return self.datefrom("%B %d, %Y")
            else:
                return self.datefrom.strftime("%B %d, %Y") + " - " + self.dateto.strftime("%B %d %Y")
        elif self.type == "week":
            return f"Week of {self.datefrom.strftime('%B %d, %Y')}"
        elif self.type == "month":
            if self.datefrom.month == self.dateto.month:
                return self.datefrom.strftime("%B %Y")
            else:
                return self.datefrom.strftime("%B %Y") + " - " + self.dateto.strftime("%B %Y")
        elif self.type == "year":
            if self.datefrom.year == self.dateto.year:
                return str(self.datefrom.year)
            else:
                return str(self.datefrom.year) + " - " + str(self.dateto.year)
        return "unknown type"

    staticmethod
    def fromString(value: str, type: str = None):
        if type is None:
            dates = value.split("-")
            if len(dates) == 1:
                datefrom = parser.parse(value).date()
                return DateRange(datefrom, None)
            else:
                datefrom = parser.parse(dates[0]).date()
                dateto = parser.parse(dates[1]).date()
                range = DateRange(datefrom, None)
                range.dateto = dateto
                return range
        else:
            datefrom = parser.parse(value).date()
            return DateRange(datefrom, type)

    staticmethod
    def lastday(value: date, type: str = None) -> date:
        if type == "month":
            nextmonth = value + relativedelta(months = 1)
            firstofnextmonth = date(nextmonth.year, nextmonth.month, 1)
            return firstofnextmonth - relativedelta(days = 1)

    def asMonth(self):
        return DateRange(self.datefrom, "month")

    def asWeek(self):
        return DateRange(self.datefrom, "week")

    def asYear(self):
        return DateRange(self.datefrom, "year")

    def asRange(self):
        range = DateRange(self.datefrom, None)
        range.dateto = self.dateto


class Page:
    navset: List[TicketSet] = []
    navlink: str = ""
    setname: str = ""
    def __init__(self, navset, navlink, setname):
        self.navset = navset
        self.navlink = navlink
        self.setname = setname

class ListBase(Page):
    set = None
    eventdata = []
    eventindex = []
    def __init__(self, navset, navlink, set):
        super().__init__(navset, navlink, set["name"])
        self.set = set

    def FillEventData(self, datefrom: date, dateto: date):
        self.eventdata = []
        self.eventindex = []
        numtix = len(self.set["tickets"])
        for i in range(numtix):
            events = Calendar.ListEvents(self.set["tickets"][i]["id"], self.set["tickets"][i]["name"], datefrom, dateto)
            self.eventdata.append(events)
            self.eventindex.append(0)


class Row:
    date: date
    summary: str
    events: List[Event]


class List(ListBase):
    range = DateRange(date.today(), "list")
    rows = []

    def __init__(self, navset, navlink, set, datefrom=None, dateto=None):
        super().__init__(navset, navlink, set)
        if datefrom == "":
            datefrom = date.today()
        else:
            datefrom = parser.parse(datefrom).date()
        if dateto == "":
            dateto = date(2050,12,31)
        else:
            dateto = parser.parse(dateto).date()
        self.range = DateRange(datefrom=datefrom, type="list")
        self.range.dateto = dateto

    def FillRows(self):
        super().FillEventData(self.range.datefrom, self.range.dateto)
        numtix = len(self.set["tickets"])
        self.rows = []
        for index in range(len(self.eventdata[0])):
            row = {
                "start": self.eventdata[0][index]["start"].strftime("%a, %b %-d, %Y %-I %p"),
                "summary": self.eventdata[0][index]["summary"],
                "events": []
            }
            for tixindex in range(numtix):
                event = self.eventdata[tixindex][index]
                row["events"].append({
                    "calendarid": event["calendarid"],
                    "id": event["id"],
                    "name": event["name"],
                    "status": event["status"],
                    "attendee": event["attendee"]
                })
            self.rows.append(row)

class Day:
    number: str = ""
    summary: str = ""
    events = [] # : List[Event] = []


class Month(ListBase):
    range = DateRange(date.today(), "month")
    rangestr = ""
    prevmonth = ""
    nextmonth = ""
    days = None
    def __init__(self, navset, navlink, set, month: int, year: int):
        super().__init__(navset, navlink, set)
        self.range = DateRange(date(year, month, 1), "month")
        self.prevmonth = self.range.previous()
        self.nextmonth = self.range.next()
        self.rangestr = str(self.range)

    def FillDays(self):
        numtix = len(self.set["tickets"])
        self.days = [
            [{}, {}, {}, {}, {}, {}, {}],
            [{}, {}, {}, {}, {}, {}, {}],
            [{}, {}, {}, {}, {}, {}, {}],
            [{}, {}, {}, {}, {}, {}, {}],
            [{}, {}, {}, {}, {}, {}, {}],
            [{}, {}, {}, {}, {}, {}, {}],
        ]
        super().FillEventData(self.range.datefrom, self.range.dateto)
        for weeknum in range(6):
            for daynum in range(7):
                dayofmonth = (weeknum * 7) + daynum - self.range.datefrom.weekday() + 1
                if dayofmonth < 1 or dayofmonth > self.range.dateto.day:
                    self.days[weeknum][daynum] = {}
                    continue
                day = {
                    "number": str(dayofmonth),
                    "summary": "",
                    "events": [],
                }

                currdate = date(self.range.datefrom.year, self.range.datefrom.month, dayofmonth)
                for i in range(numtix):
                    if self.eventindex[i] > len(self.eventdata[i]) - 1:
                        day["events"].append({})
                    else:
                        event = self.eventdata[i][self.eventindex[i]]
                        if event["start"].date() == currdate:
                            day["summary"] = event["summary"]
                            day["events"].append({
                                "calendarid": event["calendarid"],
                                "id": event["id"],
                                "name": event["name"],
                                "status": event["status"],
                                "attendee": event["attendee"]
                            })
                            self.eventindex[i] = self.eventindex[i] + 1
                self.days[weeknum][daynum] = day


class Week(ListBase):
    range = DateRange(date.today(), "week")
    days = None

    def __init__(self, set: TicketSet, datefrom: date):
        super().__init__(set)
        self.range = DateRange(datefrom, "week")
        self.days = [Day(), Day(), Day(), Day(), Day(), Day(), Day()]


    def FillDays(self):
        super().FillEventData(self.range.datefrom, self.range.dateto)
        numtix = len(self.set.tickets)
        for weekday in range(7):
            currdate = self.range.datefrom + relativedelta(days = weekday)
            day = Day()
            day.number = str(currdate.day)
            day.summary = ""
            day.events = [numtix]
            for i in range(numtix):
                if self.eventindex[i] > len(self.eventdata[i]) - 1:
                    day.events[i] = Event()
                else:
                    event = self.eventdata[i][self.eventindex[i]]
                    if event.start.date() == currdate:
                        day.summary = event.summary
                        day.events[i] = event
                        self.eventindex[i] = self.eventindex[i] + 1
            self.days[weekday] = day


class SetEdit(Page):
    set = None
    def __init__(self, navset, navlink, set):
        super().__init__(navset, navlink, set["name"])
        self.set = set


class EventEdit(Page):
    event = None

    def __init__(self, navset, navlink, event):
        setname = ""
        for set in navset:
            for ticket in set["tickets"]:
                if ticket["id"] == event["calendarid"]:
                    setname = set["name"]
                    break
        super().__init__(navset, navlink, setname)
        event["date"] = event["start"].strftime("%A %B %-d, %Y %-I:%M %p")
        self.event = event

class ReportAvailable(Page):
    teamlookup = {
        "ANA":"Anaheim Ducks",
        "ARI":"Arizona Coyotes",
        "BOS":"Boston Bruins",
        "BUF":"Buffalo Sabres",
        "CAR":"Carolina Hurricanes",
        "CBJ":"Colorado Blue Jackets",
        "CGY":"Calgary Flames",
        "CHI":"Chicago Blackhawks",
        "COL":"Colorado Avalanche",
        "DAL":"Dallas Stars",
        "DET":"Detroit Red Wings",
        "EDM":"Edmonton Oilers",
        "FLA":"Florida Panthers",
        "LAK":"Los Angeles Kings",
        "MIN":"Minnesota Wild",
        "MTL":"Montreal Canadiens",
        "NJD":"New Jersey Devils",
        "NSH":"Nashville Predators",
        "NYI":"New York Islanders",
        "NYR":"New York Rangers",
        "OTT":"Ottawa Senators",
        "PHI":"Philadelphia Flyers",
        "PIT":"Pitsburgh Penguins",
        "SJS":"San Jose Sharks",
        "STL":"St. Louis Blues",
        "TBL":"Tampa Bay Lightning",
        "TOR":"Toronto Maple Leafs",
        "VAN":"Vancouver Canucks",
        "VGK":"Vegas Golden Knights",
        "WPG":"Winnipeg Jets",
        "WSH":"Washington Capitals",
    }

    set = None
    numtix = 0
    range = DateRange(date.today(), "list")
    messages = []
    rows = []

    def __init__(self, navset, navlink, setname, datefrom, dateto):
        super().__init__(navset, navlink, setname)
        self.set = [set for set in navset if set["name"] == setname][0]
        self.numtix = len(self.set["tickets"])
        self.range = DateRange(datefrom, "list")
        self.range.dateto = dateto

    def RunReport(self):
        tickets = []
        numevents = 0
        self.messages = []
        self.rows = []
        nhlstats = NHLStats.objects.all()
        for ticket in self.set["tickets"]:
            events = Calendar.ListEvents(ticket["id"], ticket["name"], self.range.datefrom, self.range.dateto)
            tickets.append(events)
            if numevents == 0:
                numevents = len(events)
            elif numevents != len(events):
                self.messages.append("The tickets in this set have a different number of events associated with them.  This will adversely affect results below.") 
        for index in range(numevents):
            opponent = tickets[0][index]["summary"][:3]
            start = tickets[0][index]["start"].strftime("%a, %b %-d, %Y %-I %p")
            stat = nhlstats.filter(name=opponent).values().get()
            row = {
                "start": start,
                "opponent": opponent,
                "team": self.teamlookup[opponent],
                "stat": stat,
                "available": 0,
                "interest": 0,
                "pending": 0,
                "unknown": 0,
                "reserved": 0
            }
            for tix in range(self.numtix):
                status = tickets[tix][index]["status"]
                if  status == "available":
                    row["available"] += 1
                elif status == "interest":
                    row["interest"] += 1
                elif status == "pending":
                    row["pending"] += 1
                elif status == "unknown":
                    row["unknown"] += 1
                else:
                    row["reserved"] += 1
            if row["reserved"] != self.numtix:
                self.rows.append(row)

class ReportByAttendee(ListBase):
    set = None
    attendees = {}
    range = None

    def __init__(self, navset, navlink, setname, datefrom, dateto):
        self.set = [set for set in navset if set["name"] == setname][0]
        super().__init__(navset, navlink, self.set)
        self.range = DateRange(datefrom, "list")
        self.range.dateto = dateto

    def RunReport(self):
        super().FillEventData(self.range.datefrom, self.range.dateto)
        self.attendees = dict()
        for i in range(len(self.set["tickets"])):
            for j in range(len(self.eventdata[i])):
                event = self.eventdata[i][j]
                if event["attendee"] is not None and event["attendee"] != "":
                    data = {
                            "sort": event["start"].strftime("%Y%m%d"),
                            "start": event["start"].strftime("%a, %b %-d, %Y %-I %p"),
                            "summary": event["summary"],
                            "paid": event["paid"],
                            "transferred": event["transferred"]
                        }
                    if event["attendee"] in self.attendees:
                        self.attendees[event["attendee"]].append(data)
                    else:
                        self.attendees[event["attendee"]] = [ data ]
        for attendee in self.attendees:
            self.attendees[attendee].sort(key= lambda e : e["sort"], reverse=False)
