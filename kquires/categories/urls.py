from django.urls import path
from .views import CategoryListView, CategoryCreateOrUpdateView, CategoryDeleteView, CategoryStatusView, CategoryVisibilityView, category_detail_api, export_csv
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

app_name = "categories"
urlpatterns = [
    path("list/", CategoryListView.as_view(), name="list"),
    path("create/", CategoryCreateOrUpdateView.as_view(), name="create"),
    path("delete/<int:id>/", CategoryDeleteView.as_view(), name="delete"),
    path("status/<int:id>/", CategoryStatusView.as_view(), name="status"),
    path('visibility/<int:id>/', CategoryVisibilityView.as_view(), name='visibility'),
    path('api/detail/<int:id>/', category_detail_api, name='category_detail_api'),
    path('export/', export_csv, name='export_csv'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_UPLOADS)
 