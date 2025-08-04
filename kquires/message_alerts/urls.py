from django.urls import path
from django.views.generic import TemplateView
from .views import MessageAlertListView, MessageAlertCreateOrUpdateView, MessageAlertDeleteView, MessageAlertVisibilityView, message_alert_detail_api

app_name = "message_alerts"
urlpatterns = [
    path("list/", MessageAlertListView.as_view(), name="list"),
    path("create/", MessageAlertCreateOrUpdateView.as_view(), name="create"),
    path("delete/<int:id>/", MessageAlertDeleteView.as_view(), name="delete"),
    path('visibility/<int:id>/', MessageAlertVisibilityView.as_view(), name='visibility'),
    path('api/detail/<int:id>/', message_alert_detail_api, name='message_alert_detail_api'),
]