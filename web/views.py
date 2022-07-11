from datetime import date
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import HttpResponse
from web.models import *
from web.utils import getNavSets

def index(request):
    model = Home()
    model.navsets = getNavSets(request)
    model.navlink = "eventslist"

    return render(request, "web/index.html", model_to_dict(model))

def newset(request): # Create new ticket set
    pass

def editset(request): # Add ticket to a set
    pass

def eventslist(request): # Display events for ticket(s) in list form
    return HttpResponse("This is the list page")

def eventsmonth(request, name = "", value=""): # Display events for ticket(s) in month form
    return HttpResponse(f"This is the month page for set {name} in {value}")

def eventsweek(request): # Display events for ticket(s) in week form
    return HttpResponse("This is the week page")

def eventdisplay(request): # Show single event for ticket(s)
    pass

def eventedit(request): # Modify single event for ticket(s)
    pass