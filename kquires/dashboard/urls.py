from django.urls import path
from .views import search_results_view,search_articles, DashboardIndexView, DashboardHomeView, DashboardStatisticsView
from django.views.generic import TemplateView

app_name = "dashboard"
urlpatterns = [ 
    path("", DashboardIndexView.as_view(), name="index"),
    path("home/", DashboardHomeView.as_view(), name="home"),
    path("statistics/", DashboardStatisticsView.as_view(), name="statistics"),
    path("search/", search_articles, name="search_articles"),
    path('search-results/', search_results_view, name='search_results_view'), 
    
]
