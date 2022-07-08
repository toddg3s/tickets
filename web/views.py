from datetime import date
from django.shortcuts import render
from django.http import HttpResponse
from web.models import *
from web.utils import getNavSets

def index(request):
    model = Home()
    model.navsets = getNavSets(request)
    model.navlink = "eventslist"

    return render(request, "web/index.html", model)

def newset(request): # Create new ticket set
    pass

def editset(request): # Add ticket to a set
    pass

def eventslist(request): # Display events for ticket(s) in list form
    pass

def eventsmonth(request): # Display events for ticket(s) in month form
    pass

def eventsweek(request): # Display events for ticket(s) in week form
    pass

def eventdisplay(request): # Show single event for ticket(s)
    pass

def eventedit(request): # Modify single event for ticket(s)
    pass