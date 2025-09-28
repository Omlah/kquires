from django.urls import path
from .views import (
    ChatbotView, 
    send_message, 
    get_chat_history, 
    clear_chat_history,
    send_role_based_message,
    get_role_suggestions,
    get_role_articles
)

app_name = "chatbot"
urlpatterns = [
    path("", ChatbotView.as_view(), name="chat"),
    path("api/send-message/", send_message, name="send_message"),
    path("api/history/<str:session_id>/", get_chat_history, name="chat_history"),
    path("api/clear-history/", clear_chat_history, name="clear_history"),
    
    # Role-based endpoints
    path("api/send-role-based-message/", send_role_based_message, name="send_role_based_message"),
    path("api/role-suggestions/", get_role_suggestions, name="role_suggestions"),
    path("api/role-articles/", get_role_articles, name="role_articles"),
]
