from django.urls import path
from django.views.generic import TemplateView
from .views import LogsListView, export_activity_log_excel

app_name = "logs"
urlpatterns = [
   
    path("list/", LogsListView.as_view(), name="list"),
    path('export/', export_activity_log_excel, name='export_activity_log_excel'),
    
    
]




      

