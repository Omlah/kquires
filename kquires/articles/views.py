from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, View
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.utils.html import strip_tags
from django.utils.translation import get_language
from django.views.decorators.csrf import csrf_exempt
from .models import Article
from .forms import ArticleForm
from ..notifications.models import Notification
from ..utils.translation_service import detect_language, translate_text, clean_ai_json
import csv
import os
from io import TextIOWrapper
from openpyxl import Workbook
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.text import get_valid_filename
import uuid
from PyPDF2 import PdfReader
from openpyxl import load_workbook


class ArticleIndexView(DetailView):
    model = Article
    template_name = "articles/index.html"
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()

        # Strip unwanted bootstrap attrs
        if article.brief_description:
            article.brief_description = article.brief_description.replace(
                'data-bs-ride="true"', ""
            )

        # Add multi-language context
        context["article_title"] = article.title
        context["translations"] = Article.objects.filter(parent_article=article)
        context["current_language"] = article.language or get_language()

        return context


class ArticleListView(ListView):
    model = Article
    template_name = "articles/list.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(parent_article__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_language"] = get_language()
        return context


class ArticleCreateOrUpdateView(CreateView, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/create_or_update.html"

    def form_valid(self, form):
        instance = form.save(commit=False)

        # Detect language
        detected_lang = detect_language(instance.title)
        instance.language = detected_lang

        # If creating, store translation request
        if not instance.pk:
            target_lang = "ar" if detected_lang == "en" else "en"
            instance._translation_data = {
                "translated_title": translate_text(instance.title, target_lang),
                "translated_short_desc": translate_text(instance.short_description, target_lang),
                "translated_brief_desc": translate_text(instance.brief_description, target_lang),
                "target_language": target_lang,
                "detected_language": detected_lang,
            }

        instance.save()
        return redirect("articles:list")


class ArticleDeleteView(DeleteView):
    model = Article
    success_url = "/articles/list/"


class ArticleStatusView(View):
    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        new_status = request.POST.get("status")

        if new_status and new_status in ["pending", "approved", "rejected"]:
            old_status = article.status
            article.status = new_status
            article.save()

            if old_status != new_status and new_status in ["approved", "rejected"]:
                Notification.objects.create(
                    user=article.user,
                    article=article,
                    message=f"Your article '{article.title}' has been {new_status}.",
                )

        return redirect("articles:list")


class ArticleVisibilityView(View):
    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        visibility = request.POST.get("visibility")
        if visibility in ["public", "private"]:
            article.visibility = visibility
            article.save()
        return redirect("articles:list")


def article_detail_api(request, id):
    """Return article in correct language, fallback if not available"""
    article = get_object_or_404(Article, id=id)
    current_lang = get_language()

    # Try to get translation for current language
    if article.language != current_lang:
        translation = Article.objects.filter(
            parent_article=article, language=current_lang
        ).first()
        if translation:
            article = translation

    response = {
        "id": article.id,
        "title": article.title,
        "short_description": clean_ai_json(article.short_description),
        "brief_description": clean_ai_json(article.brief_description),
        "language": article.language,
        "has_english": Article.objects.filter(parent_article=article, language="en").exists(),
        "has_arabic": Article.objects.filter(parent_article=article, language="ar").exists(),
    }
    return JsonResponse(response)


class ArticlesOverviewView(ListView):
    model = Article
    template_name = "articles/overview.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(status="approved", parent_article__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_language"] = get_language()
        return context


def upload_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)

            detected_lang = detect_language(article.title)
            article.language = detected_lang
            article.save()

            # Generate translation in opposite language
            target_lang = "ar" if detected_lang == "en" else "en"
            try:
                translated_article = Article(
                    title=translate_text(article.title, target_lang),
                    short_description=translate_text(article.short_description, target_lang),
                    brief_description=translate_text(article.brief_description, target_lang),
                    user=article.user,
                    language=target_lang,
                    original_language=detected_lang,
                    parent_article=article,
                    ai_translated=True,
                    translation_status="translated",
                    category=article.category,
                    subcategory=article.subcategory,
                    status=article.status,
                    visibility=article.visibility,
                )
                translated_article.save()
            except Exception:
                import traceback
                traceback.print_exc()

            return redirect("articles:list")
    else:
        form = ArticleForm()
    return render(request, "articles/upload.html", {"form": form})


def export_xls(request):
    """Export articles to Excel format"""
    # Create a new Excel workbook and sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Articles"

    # Add headers to the sheet
    headers = ['ID', 'Title', 'Status', 'Category', 'Short Description', 'Brief Description', 'By', 'Created At']
    ws.append(headers)

    # Get data from the database
    articles = Article.objects.filter(parent_article__isnull=True)

    # Write data to the Excel sheet
    for article in articles:
        ws.append([
            article.id,
            article.title,
            article.status,
            article.category.name if article.category else '',
            article.short_description,
            article.brief_description,
            article.user.name if article.user else '',
            article.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    # Create an HTTP response with an Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=articles.xlsx'

    # Save the workbook to the response
    wb.save(response)
    return response


def export_csv(request):
    """Export articles to CSV format"""
    # Define the response as a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="articles.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['ID', 'Title', 'Status', 'Category', 'Short Description', 'Brief Description', 'By', 'Created At'])

    # Write data rows
    articles = Article.objects.filter(parent_article__isnull=True)
    for article in articles:
        writer.writerow([
            article.id,
            article.title,
            article.status,
            article.category.name if article.category else '',
            article.short_description,
            article.brief_description,
            article.user.name if article.user else '',
            article.created_at
        ])

    return response


@csrf_exempt
def process_file(request):
    """Process uploaded files (PDF, CSV, Excel, images, videos)"""
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_type = uploaded_file.content_type

        try:
            # Handle Image Uploads
            if file_type.startswith("image/"):
                safe_filename = get_valid_filename(uploaded_file.name)
                unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
                save_path = os.path.join("articles", unique_filename)
                path = default_storage.save(save_path, ContentFile(uploaded_file.read()))
                image_url = settings.MEDIA_URL + path
                return JsonResponse({"image_url": image_url})

            # Handle Video Uploads
            elif file_type.startswith("video/"):
                safe_filename = get_valid_filename(uploaded_file.name)
                unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
                save_path = os.path.join("videos", unique_filename)
                path = default_storage.save(save_path, ContentFile(uploaded_file.read()))
                video_url = settings.MEDIA_URL + path
                return JsonResponse({"video_url": video_url})

            # Handle PDF Uploads
            elif file_type == "application/pdf":
                pdf_reader = PdfReader(uploaded_file)
                content = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
                return JsonResponse({"content": content})

            # Handle CSV Uploads
            elif file_type == "text/csv":
                csv_reader = csv.reader(TextIOWrapper(uploaded_file.file, encoding="utf-8"))
                content = "\n".join([", ".join(row) for row in csv_reader])
                return JsonResponse({"content": content})

            # Handle Excel Uploads
            elif file_type in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel"
            ]:
                workbook = load_workbook(uploaded_file)
                sheet = workbook.active
                rows = [", ".join(map(str, row)) for row in sheet.iter_rows(values_only=True)]
                content = "\n".join(rows)
                return JsonResponse({"content": content})

            else:
                return JsonResponse({"error": "Unsupported file type"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
