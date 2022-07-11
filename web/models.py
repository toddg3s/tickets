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


class Home(TicketsBase):
    pass


class MultiView(TicketsBase):
    tickets = []
    daterange = None


class SingleView(TicketsBase):
    tickets = []
    eventdate = date.today()