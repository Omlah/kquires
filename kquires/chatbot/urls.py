from django.urls import path
from .views import ChatbotView, send_message, get_chat_history, clear_chat_history

app_name = "chatbot"
urlpatterns = [
    path("", ChatbotView.as_view(), name="chat"),
    path("api/send-message/", send_message, name="send_message"),
    path("api/history/<str:session_id>/", get_chat_history, name="chat_history"),
    path("api/clear-history/", clear_chat_history, name="clear_history"),
]
