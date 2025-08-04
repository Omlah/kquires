from django.urls import path

from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view
from .views import UserDeleteView
from .views import LoginView, export_csv, UserProfileView, UserPasswordResetView, UserListView, UserCreateOrUpdateView, UserUploadView, user_detail_api, SignupView
from django.views.generic import TemplateView

from django.conf import settings
from allauth import app_settings as allauth_app_settings
from . import views

app_name = "users"
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("signup/",SignupView.as_view(), name="account_signup"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("password_reset/", UserPasswordResetView.as_view(), name="password_reset"),
    path("list/", UserListView.as_view(), name="list"),
    path("create/", UserCreateOrUpdateView.as_view(), name="create"),
    path('api/detail/<int:id>/', user_detail_api, name='user_detail_api'),
    path("upload/", UserUploadView.as_view(), name="upload"),
    path("export_csv/", export_csv, name="export_csv"),
    path('delete/<int:id>/', UserDeleteView.as_view(), name='delete'),

]
