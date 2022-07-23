from datetime import date
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views.generic import FormView
from web.models import *
from web.types import *
from web.utils import getNavSets, getNavLink
from web.cal import Calendar
import json

def index(request):
    navsets = getNavSets(request)
    # with open('web/nhlstats.csv') as f:
    #     lines = f.readlines()
    #     for line in lines:
    #         parts = line.split(",")
    #         stats = NHLStats()
    #         stats.name = parts[0]
    #         stats.rank = parts[1]
    #         stats.record = parts[2]
    #         stats.vssea = parts[3]
    #         stats.playoffs = parts[4]
    #         stats.save()
    page = Home(navsets, getNavLink(request), navsets[0]["name"] if len(navsets) > 0 else "none")
    return render(request, "web/index.html", page.__dict__)

def eventslist(request, setname = "", datefrom = "", dateto = ""): # Display events for ticket(s) in list form
    navsets = getNavSets(request)
    navlink = getNavLink(request)
    set = [set for set in navsets if set['name'] == setname][0]
    page = List(navsets, navlink, set, datefrom, dateto)
    page.FillRows()
    return render(request, "web/eventslist.html", page.__dict__)

def eventsmonth(request, setname = "", datefrom=""): # Display events for ticket(s) in month form
    navsets = getNavSets(request)
    month = date.today().month
    year = date.today().year
    if datefrom != "":
        dfrom = parser.parse(datefrom)
        month = dfrom.month
        year = dfrom.year

    set = [set for set in navsets if set['name'] == setname][0]
    page = Month(navsets, "eventsmonth", set, month, year)
    page.FillDays()
    return render(request, "web/eventsmonth.html", page.__dict__)

def eventsweek(request, setname = "", datefrom = ""): # Display events for ticket(s) in week form
    navsets = getNavSets(request)
    dfrom = date.today()
    if datefrom != "":
        dfrom = parser.parse(datefrom).date()
    set = [set for set in navsets if set['name'] == setname][0]
    page = Week(navsets, "eventsweek", set, dfrom)
    page.FillDays()
    return render(request, "web/eventsweek.html", page.__dict__)    

def reportselect(request):
    return HttpResponse("reports selector")

def reportsreset(request, setname = ""):
    navset = getNavSets(request)
    set = [set for set in navset if set["name"] == setname][0]
    for ticket in set["tickets"]:
        events = Calendar.ListEvents(ticket["id"], ticket["name"], date(2000,1,1), date(2050, 12, 31))
        for event in events:
            if event["status"] == "unknown":
                event["status"] = "available"
                Calendar.UpdateEvent(event)
    return HttpResponse("Statuses reset")

def reportsavailable(request, setname = ""):
    page = ReportAvailable(getNavSets(request), getNavLink(request), setname, date.today(), date(2050,12,31))
    page.RunReport()
    return render(request, "web/reportavailable.html", page.__dict__)

def reportsbyattendee(request, setname = ""):
    page = ReportByAttendee(getNavSets(request), getNavLink(request), setname, date(2000,1,1), date(2050,1,1))
    page.RunReport()
    return render(request, "web/reportattendee.html", page.__dict__)

class EditEvent(FormView):
    def get(self, request, *args, **kwargs):
        event = Calendar.GetEvent(kwargs["calendarid"], kwargs["eventid"])
        page = EventEdit(getNavSets(request), getNavLink(request), event)
        page.event["today"] = date.today().strftime("%Y-%m-%d")
        page.event["start"] = ""
        page.event["end"] = ""
        print("before")
        print(json.dumps(page.event, indent=4))
        return render(request, "web/eventedit.html", page.__dict__)

    def post(self, request, *args, **kwargs):
        for key in request.POST:
            print(f"{key} = {request.POST[key]}")
        event = {
            "calendarid": kwargs["calendarid"],
            "id": kwargs["eventid"],
            "startts": request.POST["startts"],
            "endts": request.POST["endts"],
            "status": request.POST["status"],
            "attendee": request.POST["attendee"],
            "paid": ("paid" in request.POST and request.POST["paid"] == "on"),
            "transferred": ("transferred" in request.POST and request.POST["transferred"] == "on"),
            "interest": ""
        }
        if "interest" in request.POST:
            event["interest"] = request.POST["interest"]
        print("after")
        print(json.dumps(event, indent=4))
        Calendar.UpdateEvent(event)
        return HttpResponse("OK")


class EditSet(FormView):
    def get(self, request, *args, **kwargs):
        navsets = getNavSets(request)
        setname = kwargs['setname']
        sets = [set for set in navsets if set['name'] == setname]
        set = None
        if len(sets) == 1:
            set = sets[0]
        else:
            newset = TicketSet(name = setname)
            newset.save()
            set = newset.as_dict()
            navsets.append(set)
            request.session['navsets'] = navsets
        page = SetEdit(navsets, 'editset', set)
        return render(request, "web/editset.html", page.__dict__)

    def post(self, request, *args, **kwargs):
        setname = kwargs['setname']
        set = TicketSet.objects.get(name = setname)
        action = request.POST['submit']
        if action == "Add":
            ticket = Ticket(id = request.POST["id"], name = request.POST["name"], face=0)
            ticket.save()
            set.tickets.add(ticket)
            set.save()
        if action == "Update":
            ticket = Ticket.objects.get(id=request.POST["id"])
            ticket.name = request.POST["name"]
            ticket.save()
        if action == "Delete":
            ticket = Ticket.objects.get(id=request.POST["id"])
            ticket.delete()
        request.session["navsets"] = None
        page = SetEdit(getNavSets(request), getNavLink(request), set.as_dict())
        return render(request, "web/editset.html", page.__dict__)
