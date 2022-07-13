from web.models import TicketSet, Ticket

def getNavSets(request):
    if "navsets" in request.session and request.session["navsets"]:
        return request.session["navsets"]
    else:
        result = TicketSet.objects.all()
        navsets = [s.as_dict() for s in result]
        request.session["navsets"] = navsets
        return navsets

def getNavLink(request):
    if "navlink" in request.session and request.session["navlink"]:
        return request.session["navlink"]
    else:
        request.session["navlink"] = "eventsmonth"
        return request.session["navlink"]