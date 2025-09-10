from django.urls import path
from .views import upload_article
from django.views.generic import TemplateView
from .views import export_xls
from .views import process_file,ArticlesOverviewView, ArticleListView, ArticleCreateOrUpdateView, ArticleDeleteView, ArticleStatusView, ArticleVisibilityView, ArticleIndexView, article_detail_api, export_csv
from .api_views import translate_article_view, get_task_status

app_name = "articles"
urlpatterns = [
    path("<int:pk>/", ArticleIndexView.as_view(), name="index"),
    path("list/", ArticleListView.as_view(), name="list"),
    path("create/", ArticleCreateOrUpdateView.as_view(), name="create"),
    path("status/<int:id>/", ArticleStatusView.as_view(), name="status"),
    path('visibility/<int:id>/', ArticleVisibilityView.as_view(), name='visibility'),
    path("delete/<int:id>/", ArticleDeleteView.as_view(), name="delete"),
    path('api/detail/<int:id>/', article_detail_api, name='article_detail_api'),
    path('export/', export_csv, name='export_csv'),
    path('export/xls/', export_xls, name='export_activity_log_excel'),

    
    path('process_file/', process_file, name='process_file'),
    path('table/', ArticlesOverviewView.as_view(), name='table_overview'),


    # Other URL patterns
    path('upload/', upload_article, name='upload_article'),  # Add by me
    
    # Translation API endpoints
    path('api/translate/<int:article_id>/', translate_article_view, name='translate_article'),
    path('api/task-status/<str:task_id>/', get_task_status, name='get_task_status'),
]







 