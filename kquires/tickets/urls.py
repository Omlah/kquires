from django.urls import path

from .views import TicketListView, MyTicketListView, TicketCreateOrUpdateView, ticket_detail_api, TicketStatusUpdateView

app_name = "tickets"
urlpatterns = [
    path("list/", TicketListView.as_view(), name="list"),
    path("my_list/", MyTicketListView.as_view(), name="my_list"),
    path("create/", TicketCreateOrUpdateView.as_view(), name="create"),
    path('api/detail/<int:id>/', ticket_detail_api, name='ticket_detail_api'),
    path("status/<int:id>/", TicketStatusUpdateView.as_view(), name="status"),
]
