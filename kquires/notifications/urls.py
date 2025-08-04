from django.urls import path
from .views import get_notifications, mark_notifications_as_read, clear_all_notifications, view_all_notifications

app_name = "notifications"  # This is required for the namespace

urlpatterns = [
    path('get-notifications/', get_notifications, name='get_notifications'),
    path('mark-as-read/', mark_notifications_as_read, name='mark_notifications_as_read'),
    path('clear-all/', clear_all_notifications,name ='clear_all_notifications'),
    path('view-all/', view_all_notifications,name ='view_all_notifications'),
]
