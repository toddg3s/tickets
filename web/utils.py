from web.models import TicketSet, Ticket

def getNavSets(request):
    if request.session["navsets"]:
        return request.session["navsets"]
    else:
        navsets = TicketSet.objects.all()
        request.session["navsets"] = navsets
        return navsets
