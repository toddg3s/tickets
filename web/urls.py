from django.urls import path
from web import views

urlpatterns = [
    path("", views.index, name="home"),
    path("set/<str:setname>/edit", views.EditSet.as_view(), name="editset"),
    path("set/<str:setname>/list", views.eventslist, name="eventslist"),
    path("set/<str:setname>/list/<str:datefrom>", views.eventslist, name="eventslistfrom"),
    path("set/<str:setname>/list/<str:datefrom>/<str:dateto>", views.eventslist, name="eventslistfromto"),
    path("set/<str:setname>/month", views.eventsmonth, name="eventsmonth"),
    path("set/<str:setname>/month/<str:datefrom>", views.eventsmonth, name="eventsmonthvalue"),
    path("set/<str:setname>/week", views.eventsweek, name="eventsweek"),
    path("set/<str:setname>/week/<str:datefrom>", views.eventsweek, name="ventsweekvalue"),
    path("event", views.eventdisplay, name="eventdisplay"),
    path("event/edit", views.eventedit, name="eventedit"),
]
