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

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class TicketSet(models.Model):
    name = models.CharField(max_length=300)
    tickets = models.ManyToManyField(Ticket)

    def as_dict(self):
        tix = [t.as_dict() for t in self.tickets.all()]
        tix.sort(key = lambda t: t["name"], reverse=False)
        return {
            "name": self.name,
            "tickets": tix
        }

class NHLStats(models.Model):
    name = models.CharField(max_length=3, primary_key=True)
    rank = models.CharField(max_length=2)
    record = models.CharField(max_length=10)
    vssea = models.CharField(max_length=10)
    playoffs = models.CharField(max_length=30)