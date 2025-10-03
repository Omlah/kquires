from django.urls import path
from django.views.generic import TemplateView
from .views import (
    upload_article,
    export_xls,
    process_file,
    ArticlesOverviewView,
    ArticleListView,
    ArticleCreateView,
    ArticleUpdateView,
    ArticleDeleteView,
    ArticleStatusView,
    ArticleVisibilityView,
    ArticleIndexView,
    article_detail_api,
    export_csv,
    test_translation_api,
    FileManagerView,
    delete_file_from_drive,
    get_file_info,
    upload_pdf,
    extract_pdf_text,
    delete_pdf_file,
    search_files,
)
from .api_views import translate_article_view, get_task_status  # Added from feature branch

app_name = "articles"

urlpatterns = [
    path("<int:pk>/", ArticleIndexView.as_view(), name="index"),
    path("list/", ArticleListView.as_view(), name="list"),
    path("create/", ArticleCreateView.as_view(), name="create"),
    path("update/<int:pk>/", ArticleUpdateView.as_view(), name="update"),
    path("status/<int:id>/", ArticleStatusView.as_view(), name="status"),
    path("visibility/<int:id>/", ArticleVisibilityView.as_view(), name="visibility"),
    path("delete/<int:id>/", ArticleDeleteView.as_view(), name="delete"),
    path("api/detail/<int:id>/", article_detail_api, name="article_detail_api"),
    path("export/", export_csv, name="export_csv"),
    path("export/xls/", export_xls, name="export_activity_log_excel"),
    path("process_file/", process_file, name="process_file"),
    path("table/", ArticlesOverviewView.as_view(), name="table_overview"),

    # Upload article
    path("upload/", upload_article, name="upload_article"),

    # Translation API endpoints (from feature/article-multi-languages)
    path("api/translate/<int:article_id>/", translate_article_view, name="translate_article"),
    path("api/task-status/<str:task_id>/", get_task_status, name="get_task_status"),
    
    # Test endpoint
    path("api/test-translation/", test_translation_api, name="test_translation"),
    
    # File Manager endpoints
    path("files/", FileManagerView.as_view(), name="file_manager"),
    path("files/delete/<int:article_id>/", delete_file_from_drive, name="delete_file_from_drive"),
    path("files/info/<int:article_id>/", get_file_info, name="get_file_info"),
    
    # PDF Management endpoints
    path("upload-pdf/", upload_pdf, name="upload_pdf"),
    path("extract-pdf-text/", extract_pdf_text, name="extract_pdf_text"),
    path("delete-pdf/<int:file_id>/", delete_pdf_file, name="delete_pdf_file"),
    path("search-files/", search_files, name="search_files"),
]
