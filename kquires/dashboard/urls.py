from django.urls import path
from .views import DashboardIndexView, DashboardHomeView, DashboardStatisticsView
from django.views.generic import TemplateView

app_name = "dashboard"
urlpatterns = [ 
    path("", DashboardIndexView.as_view(), name="index"),
    path("home/", DashboardHomeView.as_view(), name="home"),
    path("statistics/", DashboardStatisticsView.as_view(), name="statistics"),
]
