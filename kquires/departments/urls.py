from django.urls import path
from .views import DepartmentCreateOrUpdateView, UserDepartmentCreateOrUpdateView,UserDepartmentDelete

app_name = "departments"
urlpatterns = [
    path("create/", DepartmentCreateOrUpdateView.as_view(), name="create"),
    path("delete/<int:id>/", UserDepartmentDelete.as_view(), name="user.delete"),
    path("user/create/", UserDepartmentCreateOrUpdateView.as_view(), name="user.create"),
]
 