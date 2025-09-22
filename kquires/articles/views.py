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
from ..categories.models import Category
from ..utils.translation_service import detect_language, translate_text, clean_ai_json

def get_translated_text(text, source_lang, target_lang):
    """Helper function to get translated text"""
    if not text:
        return text
    
    try:
        # Test if AI service is available
        from kquires.articles.ai_services import ai_service
        if not ai_service.client:
            print("AI service client not available")
            raise Exception("AI service not available")
        
        # Test with a simple translation first
        test_result = ai_service.translate_content("Hello", "english", "arabic")
        if 'error' in test_result:
            print(f"AI service test failed: {test_result['error']}")
            raise Exception(f"AI service test failed: {test_result['error']}")
        
        result = translate_text(text, source_lang, target_lang)
        print(f"Translation result for '{text[:50]}...': {result}")  # Debug log
        
        if isinstance(result, dict):
            if 'error' in result:
                print(f"Translation error: {result['error']}")
                raise Exception(f"Translation failed: {result['error']}")
            translated = result.get('translated_text', text)
            if translated == text and source_lang != target_lang:
                raise Exception("Translation returned original text")
            return translated
        else:
            return result
    except Exception as e:
        print(f"Translation exception: {e}")
        raise e
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
        return Article.objects.filter(parent_article__isnull=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_language"] = get_language()
        context['categories'] = Category.objects.filter(status='approved', type='Main')
        return context


class ArticleCreateView(CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/create_or_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(status='approved', type='Main')
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)

        # Detect language
        detected_lang = detect_language(instance.title)
        instance.language = detected_lang
        instance.save()
        
        # Generate translation in opposite language
        target_lang = "arabic" if detected_lang == "english" else "english"
        
        try:
            # Check if translation already exists
            existing_translation = Article.objects.filter(
                parent_article=instance, 
                language=target_lang
            ).first()
            
            if existing_translation:
                # Update existing translation
                existing_translation.title = get_translated_text(instance.title, instance.language, target_lang)
                existing_translation.short_description = get_translated_text(instance.short_description, instance.language, target_lang)
                existing_translation.brief_description = get_translated_text(instance.brief_description, instance.language, target_lang)
                existing_translation.category = instance.category
                existing_translation.subcategory = instance.subcategory
                existing_translation.status = instance.status
                existing_translation.visibility = instance.visibility
                existing_translation.save()
            else:
                # Create new translation
                translated_article = Article(
                    title=get_translated_text(instance.title, instance.language, target_lang),
                    short_description=get_translated_text(instance.short_description, instance.language, target_lang),
                    brief_description=get_translated_text(instance.brief_description, instance.language, target_lang),
                    user=instance.user,
                    language=target_lang,
                    original_language=detected_lang,
                    parent_article=instance,
                    ai_translated=True,
                    translation_status="translated",
                    category=instance.category,
                    subcategory=instance.subcategory,
                    status=instance.status,
                    visibility=instance.visibility,
                )
                translated_article.save()
        except Exception:
            import traceback
            traceback.print_exc()

        return redirect("articles:list")


class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/create_or_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(status='approved', type='Main')
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save()
        
        # Update translation in opposite language if it exists
        main_article = instance.parent_article if instance.parent_article else instance
        target_lang = "arabic" if instance.language == "english" else "english"
        
        try:
            existing_translation = Article.objects.filter(
                parent_article=main_article, 
                language=target_lang
            ).first()
            
            if existing_translation:
                # Update existing translation
                existing_translation.title = get_translated_text(instance.title, instance.language, target_lang)
                existing_translation.short_description = get_translated_text(instance.short_description, instance.language, target_lang)
                existing_translation.brief_description = get_translated_text(instance.brief_description, instance.language, target_lang)
                existing_translation.category = instance.category
                existing_translation.subcategory = instance.subcategory
                existing_translation.status = instance.status
                existing_translation.visibility = instance.visibility
                existing_translation.save()
        except Exception:
            import traceback
            traceback.print_exc()
        
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
    requested_lang = request.GET.get('language', 'english')
    # Get the main article (parent or self)
    main_article = article.parent_article if article.parent_article else article
    
    # Try to get translation for requested language
    if article.language != requested_lang:
        translation = Article.objects.filter(
            parent_article=main_article, language=requested_lang
        ).first()
        if translation:
            article = translation
        else:
            # If translation doesn't exist, try to create it on the fly
            try:
                print(f"Creating translation for article {main_article.id} from {main_article.language} to {requested_lang}")
                
                if requested_lang == "arabic":
                    translated_title = get_translated_text(main_article.title, main_article.language, "arabic")
                    translated_short_desc = get_translated_text(main_article.short_description, main_article.language, "arabic")
                    translated_brief_desc = get_translated_text(main_article.brief_description, main_article.language, "arabic")
                else:  # english
                    translated_title = get_translated_text(main_article.title, main_article.language, "english")
                    translated_short_desc = get_translated_text(main_article.short_description, main_article.language, "english")
                    translated_brief_desc = get_translated_text(main_article.brief_description, main_article.language, "english")
                
                print(f"Translated title: {translated_title}")
                print(f"Translated short_desc: {translated_short_desc}")
                print(f"Translated brief_desc: {translated_brief_desc}")
                
                # Create the translation
                translation = Article.objects.create(
                    title=translated_title,
                    short_description=translated_short_desc,
                    brief_description=translated_brief_desc,
                    user=main_article.user,
                    language=requested_lang,
                    original_language=main_article.language,
                    parent_article=main_article,
                    ai_translated=True,
                    translation_status="translated",
                    category=main_article.category,
                    subcategory=main_article.subcategory,
                    status=main_article.status,
                    visibility=main_article.visibility,
                )
                article = translation
                print(f"Translation created successfully with ID: {translation.id}")
            except Exception as e:
                # If translation fails, don't create article, just return original with status
                print(f"Translation failed: {e}")
                import traceback
                traceback.print_exc()
                # Set flag to indicate translation failed
                translation_in_progress = True

    # Check if the content is actually translated or still in English
    is_translated = True
    translation_in_progress = False
    
    # Check if we're dealing with a failed translation attempt or not translated
    if (article.language == requested_lang and article.title == main_article.title) or article.translation_status == 'not_translated':
        # This means we're trying to get a translation but got the original content
        translation_in_progress = True
        is_translated = False
    
    # If translation is in progress, return original content with status
    if translation_in_progress:
        response = {
            "id": main_article.id,  # Return main article ID
            "main_id": main_article.id,
            "title": main_article.title,  # Return original content
            "short_description": clean_ai_json(main_article.short_description),
            "brief_description": clean_ai_json(main_article.brief_description),
            "language": main_article.language,  # Return original language
            "current_language": main_article.language,
            "category_id": main_article.category.id if main_article.category else None,
            "subcategory_id": main_article.subcategory.id if main_article.subcategory else None,
            "has_english": Article.objects.filter(parent_article=main_article, language="english").exists(),
            "has_arabic": Article.objects.filter(parent_article=main_article, language="arabic").exists(),
            "is_translated": False,
            "translation_status": "translation_in_progress",
            "translation_message": f"Translation to {requested_lang} is not available. Please check your OpenAI API key configuration in the .env file."
        }
    else:
        response = {
            "id": article.id,
            "main_id": main_article.id,
            "title": article.title,
            "short_description": clean_ai_json(article.short_description),
            "brief_description": clean_ai_json(article.brief_description),
            "language": article.language,
            "current_language": article.language,
            "category_id": article.category.id if article.category else None,
            "subcategory_id": article.subcategory.id if article.subcategory else None,
            "has_english": Article.objects.filter(parent_article=main_article, language="english").exists(),
            "has_arabic": Article.objects.filter(parent_article=main_article, language="arabic").exists(),
            "is_translated": is_translated,
            "translation_status": article.translation_status if hasattr(article, 'translation_status') else ("translated" if is_translated else "translation_in_progress")
        }
    return JsonResponse(response)


def test_translation_api(request):
    """Test endpoint to check if translation is working"""
    try:
        from kquires.articles.ai_services import ai_service
        
        if not ai_service.client:
            return JsonResponse({
                "status": "error",
                "message": "AI service client not available",
                "api_key_configured": bool(getattr(settings, 'OPENAI_API_KEY', None))
            })
        
        # Test translation
        test_text = "Hello World"
        result = ai_service.translate_content(test_text, "english", "arabic")
        
        return JsonResponse({
            "status": "success",
            "test_text": test_text,
            "translation_result": result,
            "ai_service_available": True
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "ai_service_available": False
        })


class ArticlesOverviewView(ListView):
    model = Article
    template_name = "articles/overview.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(status="approved", parent_article__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_language"] = get_language()
        context['categories'] = Category.objects.filter(status='approved', type='Main')
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
            target_lang = "arabic" if detected_lang == "english" else "english"
            try:
                # Check if translation already exists
                existing_translation = Article.objects.filter(
                    parent_article=article, 
                    language=target_lang
                ).first()
                
                if existing_translation:
                    # Update existing translation
                    existing_translation.title = get_translated_text(article.title, article.language, target_lang)
                    existing_translation.short_description = get_translated_text(article.short_description, article.language, target_lang)
                    existing_translation.brief_description = get_translated_text(article.brief_description, article.language, target_lang)
                    existing_translation.category = article.category
                    existing_translation.subcategory = article.subcategory
                    existing_translation.status = article.status
                    existing_translation.visibility = article.visibility
                    existing_translation.save()
                else:
                    # Create new translation
                    translated_article = Article(
                        title=get_translated_text(article.title, article.language, target_lang),
                        short_description=get_translated_text(article.short_description, article.language, target_lang),
                        brief_description=get_translated_text(article.brief_description, article.language, target_lang),
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
    categories = Category.objects.filter(status='approved', type='Main')
    return render(request, "articles/upload.html", {"form": form, "categories": categories})


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
