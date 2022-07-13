from datetime import date, datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
from typing import List
import re
from django.db import models
from web.models import Ticket, TicketSet
from web.cal import Event, Calendar

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
        numtix = len(self.set["tickets"])
        eventdata = [numtix]
        eventindex = [numtix]
        for i in range(numtix):
            events = Calendar.ListEvents(self.set["tickets"][i]["id"], datefrom, dateto)
            eventdata[i] = events
            eventindex[i] = 0


class Row:
    date: date
    summary: str
    events: List[Event]


class List(ListBase):
    range = DateRange(date.today(), "list")
    rows: List[Row] = []

    def __init__(self, navset, navlink, set, datefrom=None, dateto=None):
        super().__init__(navset, navlink, set.name)
        range = DateRange(datefrom=datefrom, type="list")
        range.dateto = dateto if dateto is not None else date.max

    def FillRows(self):
        super().FillEventData(self.range.datefrom, self.range.dateto)
        numtix = len(self.set.tickets)
        currdate = self.range.datefrom
        while currdate <= self.range.dateto:
            row = Row()
            row.date = currdate
            row.summary = ""
            row.events = [numtix]
            for i in range(numtix):
                event = self.eventdata[i][self.eventindex[i]]
                if event.start.date() == currdate:
                    row.summary = event.Get('summary', "")
                    row.events[i] = event
                    self.eventindex[i] = self.eventindex[i] + 1
                else:
                    row.events[i] = Event()
            currdate = currdate + relativedelta(days = 1)


class Day:
    number: str = ""
    summary: str = ""
    events = [] # : List[Event] = []


class Month(ListBase):
    range = DateRange(date.today(), "month")
    rangestr = ""
    days = None
    def __init__(self, navset, navlink, set, month: int, year: int):
        super().__init__(navset, navlink, set)
        self.range = DateRange(date(year, month, 1), "month")
        self.rangestr = str(self.range)

    def FillDays(self):
        numtix = len(self.set["tickets"])
        self.days = [
            [Day(), Day(), Day(), Day(), Day(), Day(), Day()],
            [Day(), Day(), Day(), Day(), Day(), Day(), Day()],
            [Day(), Day(), Day(), Day(), Day(), Day(), Day()],
            [Day(), Day(), Day(), Day(), Day(), Day(), Day()],
            [Day(), Day(), Day(), Day(), Day(), Day(), Day()],
        ]
        super().FillEventData(self.range.datefrom, self.range.dateto)
        monthdone = False
        for weeknum in range(5):
            for daynum in range(7):
                dayofmonth = (weeknum * 7) + daynum - self.range.datefrom.weekday() + 1
                if dayofmonth < 1 or dayofmonth > self.range.dateto.day:
                    self.days[weeknum][daynum] = Day()
                    continue
                day = Day()
                day.number = str(dayofmonth)
                day.summary = ""
                day.events = [numtix]

                currdate = date(self.range.datefrom.year, self.range.datefrom.month, dayofmonth)
                for i in range(numtix):
                    if self.eventindex[i] > len(self.eventdata[i]) - 1:
                        day.events[i] = Event()
                    else:
                        event = self.eventdata[i][self.eventindex[i]]
                        if event.start.date() == currdate:
                            day.summary = event.summary
                            day.events[i] = event
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
