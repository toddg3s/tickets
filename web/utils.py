from datetime import date, datetime
import pytz
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

def dtformat(value, format: str):
    monshort = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    dayshort = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    if type(value) is date:
        value = datetime(value.year, value.month, value.day, 0, 0, 0, 0, pytz.timezone("US/Pacific"))
    if type(value) is not datetime:
        return "not a date/time"
    if value.hour > 12:
        if value.minute == 0:
            timeval = f"{value.hour - 12}pm"
        elif value.minute < 10:
            timeval = f"{value.hour - 12}:0{value.minute}pm"
        else:
            timeval = f"{value.hour - 12}:{value.minute}pm"
    else:
        if value.minute == 0:
            timeval = f"{value.hour}pm"
        elif value.minute < 10:
            timeval = f"{value.hour}:0{value.minute}pm"
        else:
            timeval = f"{value.hour}:{value.minute}pm"

    if format == "long":
        return f"{dayshort[value.weekday()]}, {monshort[value.month]} {value.day}, {value.year} {timeval}"
    elif format == "short":
        return f"{monshort[value.month]} {value.day} {timeval}"
    
    return value.strftime(format)
