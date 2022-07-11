from web.models import TicketSet, Ticket

def getNavSets(request):
    if "navsets" in request.session and request.session["navsets"]:
        return request.session["navsets"]
    else:
        result = TicketSet.objects.all()
        for s in result:
            print(s.name)
            for t in s.tickets:
                print(t.name)
        navsets = [s for s in result]
        request.session["navsets"] = navsets
        return navsets
