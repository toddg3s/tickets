from django.urls import path
from web import views

urlpatterns = [
    path("", views.index, name="home"),
    path("set/new", views.newset, name="newset"),
    path("set/edit", views.editset, name="editset"),
    path("events/list", views.eventslist, name="eventslist"),
    path("events/month", views.eventsmonth, name="eventsmonth"),
    path("events/week", views.eventsweek, name="eventsweek"),
    path("event", views.eventdisplay, name="eventdisplay"),
    path("event/edit", views.eventedit, name="eventedit"),
]
