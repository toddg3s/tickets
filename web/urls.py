from django.urls import path
from web import views

urlpatterns = [
    path("", views.index, name="home"),
    path("set/new", views.newset, name="newset"),
    path("set/edit", views.editset, name="editset"),
    path("list", views.eventslist, name="eventslist"),
    path("set/<str:name>/month", views.eventsmonth, name="eventsmonth"),
    path("set/<str:name>/month/<str:value>", views.eventsmonth, name="eventsmonthvalue"),
    path("set/<str:name>/week", views.eventsweek, name="eventsweek"),
    path("set/<str:name>/week/<str:value>", views.eventsweek, name="ventsweekvalue"),
    path("event", views.eventdisplay, name="eventdisplay"),
    path("event/edit", views.eventedit, name="eventedit"),
]
