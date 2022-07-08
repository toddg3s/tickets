from datetime import date, datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
import re
from django.db import models


class Ticket(models.Model):
    id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)
    venue = models.CharField(max_length=300)
    section = models.CharField(max_length=20)
    row = models.CharField(max_length=20)
    seat = models.CharField(max_length=10)
    face = models.FloatField()
    events = []

    def __str__(self):
        return f"sec {self.section} row {self.row} seat {self.seat} - {self.name}"

    def loadEvents(self, range: 'DateRange'):
        pass


class TicketSet(models.Model):
    name = models.CharField(max_length=300)
    tickets = models.ManyToManyField(Ticket)


class TicketsBase(models.Model):
    navsets = []
    navlink = "eventslist"


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


class Home(TicketsBase):
    pass


class MultiView(TicketsBase):
    tickets = []
    daterange = None


class SingleView(TicketsBase):
    tickets = []
    eventdate = date.today()