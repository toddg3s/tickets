from datetime import date
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views.generic import FormView
from web.models import *
from web.types import *
from web.utils import getNavSets, getNavLink

def index(request):
    navsets = getNavSets(request)
    page = Page(navsets, getNavLink(request), navsets[0]["name"] if len(navsets) > 0 else "none")
    return render(request, "web/index.html", page.__dict__)

def eventslist(request, setname = "", datefrom = "", dateto = ""): # Display events for ticket(s) in list form
    return HttpResponse("This is the list page")

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
    print(page.__dict__)
    return render(request, "web/eventsmonth.html", page.__dict__)

def eventsweek(request, setname = "", datefrom = ""): # Display events for ticket(s) in week form
    return HttpResponse("This is the week page")

def eventdisplay(request): # Show single event for ticket(s)
    pass

def eventedit(request): # Modify single event for ticket(s)
    pass

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
