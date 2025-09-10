from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, DetailView, View
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Article
from ..categories.models import Category
from .forms import ArticleForm
from django.urls import reverse_lazy
from django.http import HttpResponse
import csv
from ..users.models import User
from django.views.decorators.csrf import csrf_exempt
from PyPDF2 import PdfReader
import csv
import os
from io import TextIOWrapper
from openpyxl import load_workbook
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.text import get_valid_filename
import uuid
from django.db.models import Q
import re

# Create your views here.
import re
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from openpyxl import Workbook
from django.http import HttpRequest


def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    related_articles = Article.objects.filter(subject=article.subject).exclude(id=article.id)[:5]  # Fetch related articles

    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'articles/index.html', context)

class ArticleIndexView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'articles/index.html'
    context_object_name = 'article'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Get current language from Django's i18n
        from django.utils import translation
        current_language = translation.get_language()
        
        # Map Django language codes to our model language codes
        language_mapping = {
            'en': 'english',
            'ar': 'arabic'
        }
        current_lang = language_mapping.get(current_language, 'english')
        
        # Get language-aware content
        context['article_title'] = article.get_title_for_language(current_lang)
        context['article_short_description'] = article.get_short_description_for_language(current_lang)
        context['article_brief_description'] = article.get_brief_description_for_language(current_lang)
        
        # Get translations
        translations = article.get_translations()
        context['translations'] = translations
        
        # Check if other language is available
        other_lang = 'arabic' if current_lang == 'english' else 'english'
        context['has_other_language'] = article.has_translation(other_lang)
        context['other_language'] = other_lang
        
        # Record click
        article.record_click()
        
        return context

    def get(self, request, *args, **kwargs):
        article = self.get_object()
        article.record_click()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        article = context["article"]


        if article.brief_description:
            article.brief_description = re.sub(r'data-bs-ride="carousel"', '', article.brief_description)

        return context

    def get_paginate_by(self, queryset: HttpRequest):
        page_size = self.request.GET.get('page_size', 10)
        try:
            return int(page_size)
        except ValueError:
            return 10


class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'articles/list.html'
    context_object_name = 'articles'
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        
        # Redirect employees or managers to the dashboard home page
        if user.is_employee or user.is_manager:
            return redirect('dashboard:index')  # Redirect to home page (dashboard/index.html)
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Show ALL parent articles regardless of language
        # The language-specific content will be handled in the template
        query = Article.objects.filter(
            Q(parent_article__isnull=True)  # Only show parent articles (not translations)
        ).order_by('-updated_at')
        
        # Debug: Print query count
        
        category_id = self.request.GET.get('category_id', None)
        sort_by = self.request.GET.get('sort_by',None)
        sort_type = self.request.GET.get('sort_type',None)
        q = self.request.GET.get("q", "").strip()
        
        if category_id:
            query = query.filter(category_id= category_id )
        if q:
            query = query.filter(Q(title__icontains=q))

        if sort_by == 'title' or sort_by == 'created_at' or sort_by == 'user':
            if sort_type=='asc':
             query=query.order_by(sort_by)
            else:
             query=query.order_by(f"-{sort_by}")

        if sort_by =='status':
            query = query.order_by(
            f"status" if sort_type == 'asc' else f"-status"
        )

        return query


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(status='approved')
        ticket_id = self.request.GET.get('id')
        if ticket_id:
            context["ticket"] = get_object_or_404(Article, id=ticket_id)
        
        # Get current language from Django's i18n
        from django.utils import translation
        current_language = translation.get_language()
        
        # Map Django language codes to our model language codes
        language_mapping = {
            'en': 'english',
            'ar': 'arabic'
        }
        current_lang = language_mapping.get(current_language, 'english')
        context['current_language'] = current_lang
        
        # Debug: Print current language
        return context

    def render_to_response(self, context, **response_kwargs):
        request = self.request
        if request.headers.get("HX-Request") == "true":
            return render(request, "articles/partials/table.html", context)
        return super().render_to_response(context, **response_kwargs)


class ArticleCreateOrUpdateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/list.html'
    success_url = reverse_lazy('articles:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article_id = self.request.GET.get('id')
        if article_id:
            context["article"] = get_object_or_404(Article, id=article_id)
        return context

    def post(self, request, *args, **kwargs):
        article_id = request.POST.get('id')
        current_language = request.POST.get('current_language', 'english')
        
        if article_id:
            # Get the main article first
            main_article = get_object_or_404(Article, id=article_id)
            
            # Determine which article to update based on current language
            if current_language == 'english':
                # Update the main article if it's in English, or find the English translation
                if main_article.language == 'english':
                    self.object = main_article
                else:
                    # Find English translation
                    english_translation = main_article.translations.filter(language='english').first()
                    if english_translation:
                        self.object = english_translation
                    else:
                        self.object = main_article  # Fallback to main article
            else:  # Arabic
                # Update the Arabic translation if it exists, or the main article if it's in Arabic
                if main_article.language == 'arabic':
                    self.object = main_article
                else:
                    # Find Arabic translation
                    arabic_translation = main_article.translations.filter(language='arabic').first()
                    if arabic_translation:
                        self.object = arabic_translation
                    else:
                        self.object = main_article  # Fallback to main article
            
            form = self.form_class(request.POST, request.FILES, instance=self.object)
            action = "updated"
        else:
            self.object = None  # ✅ Ensure `self.object` is set
            form = self.form_class(request.POST, request.FILES)
            action = "created"

        if form.is_valid():
            self.object = form.save(commit=False)  # ✅ Save object in `self.object`
            if not article_id:
                self.object.user = request.user
                
                # Auto-detect language and create translation for new articles
                self._create_automatic_translation(request)
            
            self.object.save()
            user = User.objects.get(id=self.request.user.id)
            user.log(action, f"Article successfully {action}.")
            
            # Check if translation was prepared
            if hasattr(self.object, '_translation_data'):
                detected_lang = self.object._translation_data['detected_language']
                target_lang = self.object._translation_data['target_language']
                messages.success(request, f"✅ Article successfully {action}! AI automatically detected {detected_lang} and created both {detected_lang} and {target_lang} versions.")
            else:
                messages.success(request, f"Article successfully {action}.")
            
            return self.form_valid(form)  # ✅ Call `form_valid()`
        else:
            return self.form_invalid(form)

    def _create_automatic_translation(self, request):
        """Create automatic translation for new articles"""
        try:
            from .ai_services import ai_service
            
            # Combine content for language detection
            combined_content = f"{self.object.title} {self.object.short_description} {self.object.brief_description}".strip()
            
            # Auto-detect language from content
            detected_language = 'english'  # Default
            if combined_content:
                try:
                    detected_language = ai_service.detect_language(combined_content)
                except Exception as e:
                    # Fallback: simple heuristic
                    if any('\u0600' <= char <= '\u06FF' for char in combined_content):
                        detected_language = 'arabic'
                    else:
                        detected_language = 'english'
            
            # Set the detected language
            self.object.language = detected_language
            self.object.original_language = detected_language
            
            # Generate translation to the other language
            target_language = 'arabic' if detected_language == 'english' else 'english'
            
            
            # Translate all content
            translated_title = self.object.title
            translated_short_desc = self.object.short_description
            translated_brief_desc = self.object.brief_description
            
            if self.object.title:
                title_translation = ai_service.translate_content(self.object.title, detected_language, target_language)
                if 'translated_text' in title_translation:
                    translated_title = title_translation['translated_text']
            
            if self.object.short_description:
                short_desc_translation = ai_service.translate_content(self.object.short_description, detected_language, target_language)
                if 'translated_text' in short_desc_translation:
                    translated_short_desc = short_desc_translation['translated_text']
            
            if self.object.brief_description:
                brief_desc_translation = ai_service.translate_content(self.object.brief_description, detected_language, target_language)
                if 'translated_text' in brief_desc_translation:
                    translated_brief_desc = brief_desc_translation['translated_text']
            
            # Store translation data for later use (after main article is saved)
            self.object._translation_data = {
                'target_language': target_language,
                'translated_title': translated_title,
                'translated_short_desc': translated_short_desc,
                'translated_brief_desc': translated_brief_desc,
                'detected_language': detected_language
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Continue with article creation even if translation fails

    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    error_messages.append(error)
                else:
                    error_messages.append(f"{form.fields[field].label}: {error}")

        error_message = "\n".join(error_messages)
        messages.error(self.request, error_message)
        return self.render_to_response(self.get_context_data(form=form))

def article_detail_api(request, id):
    article = Article.objects.get(id=id)
    
    # Get language parameter from request (default to current language)
    target_language = request.GET.get('language', 'english')
    
    # Find the main article (parent) if this is a translation
    main_article = article.parent_article if article.parent_article else article
    
    # Debug logging
    print(f"🔍 article_detail_api called:")
    print(f"  - Article ID: {id}")
    print(f"  - Target language: {target_language}")
    print(f"  - Article language: {article.language}")
    print(f"  - Main article ID: {main_article.id}")
    print(f"  - Main article language: {main_article.language}")
    print(f"  - Available translations: {list(main_article.translations.values_list('id', 'language'))}")
    
    # Completely rewrite the language selection logic
    print(f"🔍 Starting language selection for target: {target_language}")
    
    # First, let's find ALL articles related to this main article
    all_related_articles = Article.objects.filter(
        Q(id=main_article.id) | Q(parent_article=main_article)
    ).order_by('id')
    
    print(f"📋 All related articles:")
    for art in all_related_articles:
        print(f"  - ID: {art.id}, Language: {art.language}, Parent: {art.parent_article_id}, Title: {art.title[:30]}...")
    
    # Now find the correct article for the target language
    if target_language == 'english':
        # Look for English article
        english_article = all_related_articles.filter(language='english').first()
        if english_article:
            display_article = english_article
            print(f"✅ Found English article: {english_article.id}")
        else:
            print(f"❌ No English article found!")
            display_article = main_article
    else:
        # Look for Arabic article
        arabic_article = all_related_articles.filter(language='arabic').first()
        if arabic_article:
            display_article = arabic_article
            print(f"✅ Found Arabic article: {arabic_article.id}")
        else:
            print(f"❌ No Arabic article found!")
            display_article = main_article
    
    # Debug logging for selected article
    print(f"🎯 Selected display article:")
    print(f"  - Display article ID: {display_article.id}")
    print(f"  - Display article language: {display_article.language}")
    print(f"  - Display article title: {display_article.title[:50]}...")
    print(f"  - Display article title (raw): {repr(display_article.title[:100])}")
    print(f"  - Display article short_desc (raw): {repr(display_article.short_description[:100])}")
    
    # Helper function to extract clean text from potentially JSON-formatted fields
    def extract_clean_text(text):
        if not text:
            return text
        
        original_text = text
        # Check if the text looks like a JSON string
        if isinstance(text, str) and text.strip().startswith('{') and text.strip().endswith('}'):
            try:
                import json
                data = json.loads(text)
                # If it's a translation response, extract the translated text
                if isinstance(data, dict) and 'translated_text' in data:
                    result = data['translated_text']
                    print(f"🔧 extract_clean_text: JSON -> translated_text: {repr(result[:50])}")
                    return result
                # If it's a translation response, extract the original text
                elif isinstance(data, dict) and 'original_text' in data:
                    result = data['original_text']
                    print(f"🔧 extract_clean_text: JSON -> original_text: {repr(result[:50])}")
                    return result
            except (json.JSONDecodeError, TypeError):
                pass
        
        print(f"🔧 extract_clean_text: No change needed: {repr(text[:50])}")
        return text
    
    return JsonResponse({
        'id': display_article.id,  # Return the ID of the specific language version being displayed
        'main_id': main_article.id,  # Also return main article ID for reference
        'title': extract_clean_text(display_article.title),
        'short_description': extract_clean_text(display_article.short_description),
        'brief_description': extract_clean_text(display_article.brief_description),
        'category': display_article.category.name if display_article.category else '',
        'current_language': display_article.language,
        'has_english': main_article.language == 'english' or main_article.translations.filter(language='english').exists(),
        'has_arabic': main_article.language == 'arabic' or main_article.translations.filter(language='arabic').exists(),
    })


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    success_url = reverse_lazy('articles:list')

    def get_object(self, queryset=None):
        return get_object_or_404(Article, id=self.kwargs.get('id'))

    def delete(self, request, *args, **kwargs):
        # Add success message
        user =  User.objects.get(id=self.request.user.id)
        user.log('deleted', f"Article successfully deleted.")
        messages.success(request, "Article successfully deleted.")
        return super().delete(request, *args, **kwargs)


class ArticleStatusView(LoginRequiredMixin, View):
    success_url = reverse_lazy('articles:list')
    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, id=self.kwargs.get('id'))
        new_status = request.POST.get('status')
        new_comment = request.POST.get('comment')

        if not new_status:
            messages.error(request, "Status is required.")
            return JsonResponse({'error': 'Status is required.'}, status=400)

        article.status = new_status
        article.comment = new_comment
        article.save()

        # Add a success message
        user =  User.objects.get(id=self.request.user.id)
        user.log('updated', f"Article status updated to '{new_status}'.")
        messages.success(request, f"Article status updated to '{new_status}'.")
        return redirect(self.success_url)

class ArticleVisibilityView(LoginRequiredMixin, View):
    success_url = reverse_lazy('articles:list')
    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, id=self.kwargs.get('id'))
        new_visibility = request.POST.get('visibility')

        if new_visibility not in ['True', 'False']:
            messages.error(request, "Invalid visibility value.")
            return JsonResponse({'error': 'Invalid visibility value.'}, status=400)

        article.visibility = new_visibility == 'True'
        article.save()

        # Add a success message
        status_text = "visible" if article.visibility else "hidden"
        user =  User.objects.get(id=self.request.user.id)
        user.log('updated', f"Article status updated to {status_text}.")
        messages.success(request, f"Article is now {status_text}.")
        return redirect(self.success_url)



def export_xls(request):
    # Create a new Excel workbook and sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Articles"

    # Add headers to the sheet
    headers = ['ID', 'Title', 'Status', 'Category', 'Short Description', 'Brief Description', 'By', 'Created At']
    ws.append(headers)  # This appends the header row to the sheet

    # Get data from the database
    articles = Article.objects.all()  # Fetch all articles

    # Write data to the Excel sheet
    for article in articles:
        ws.append([
            article.id,
            article.title,
            article.status,
            article.category.name,
            article.short_description,
            article.brief_description,
            article.user.name,
            article.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    # Create an HTTP response with an Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=articles.xlsx'

    # Save the workbook to the response
    wb.save(response)

    return response





def export_csv(request):
    # Define the response as a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="activities.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['ID', 'Title', 'Status', 'Category', 'Short Description', 'Brief Description', 'By', 'Created At'])  # Adjust the fields as per your model

    # Write data rows
    articles = Article.objects.all()  # Fetch data
    for article in articles:
        writer.writerow([article.id, article.title, article.status, article.category.name, article.short_description, article.brief_description, article.user.name, article.created_at])

    return response


@csrf_exempt

def process_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_type = uploaded_file.content_type

        try:
            # ✅ **Handle Image Uploads** (Append to existing slider)
            if file_type.startswith("image/"):
                safe_filename = get_valid_filename(uploaded_file.name)
                unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
                save_path = os.path.join("articles", unique_filename)
                path = default_storage.save(save_path, ContentFile(uploaded_file.read()))
                image_url = settings.MEDIA_URL + path

                # ✅ Append new image to the article (instead of replacing)
                article_id = request.POST.get("article_id")
                if article_id:
                    article = Article.objects.get(id=article_id)
                    new_image = ArticleImage(article=article, image=path)
                    new_image.save()

                return JsonResponse({"image_url": image_url})

            # ✅ **Handle Video Uploads**
            elif file_type.startswith("video/"):
                safe_filename = get_valid_filename(uploaded_file.name)
                unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
                save_path = os.path.join("videos", unique_filename)  # Save inside 'media/videos/'
                path = default_storage.save(save_path, ContentFile(uploaded_file.read()))
                video_url = settings.MEDIA_URL + path  # Return accessible URL

                return JsonResponse({"video_url": video_url})  # ✅ Returns video URL

            # ✅ **Handle PDF Uploads**
            elif file_type == "application/pdf":
                pdf_reader = PdfReader(uploaded_file)
                content = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
                return JsonResponse({"content": content})

            # ✅ **Handle CSV Uploads**
            elif file_type == "text/csv":
                csv_reader = csv.reader(TextIOWrapper(uploaded_file.file, encoding="utf-8"))
                content = "\n".join([", ".join(row) for row in csv_reader])
                return JsonResponse({"content": content})

            # ✅ **Handle Excel Uploads**
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


class ArticlesOverviewView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'articles/table.html'
    context_object_name = 'articles'


    def get_queryset(self):
        """Retrieve only approved and visible articles."""
        query = Article.objects.filter(status='approved')
        category_id = self.request.GET.get('category_id')
        sub_category_id = self.request.GET.get('sub_category_id')
        if category_id and not sub_category_id:
            sub_cat_ids = Category.objects.filter(status='approved', type="Main", parent_category=category_id).values_list('id', flat=True)
            query = query.filter(category_id__in = [category_id] + list(sub_cat_ids))
        if sub_category_id:
            query = query.filter(category_id = sub_category_id)
        return query

    def get_context_data(self, **kwargs):
        """Add categories to the context."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(status='approved', type="Main" )
        context['subcategories'] = Category.objects.filter(status='approved', type="Sub")
        category_id = self.request.GET.get('category_id')
        sub_category_id = self.request.GET.get('sub_category_id')
        if category_id:
            context['category_id'] = int(category_id)
        if sub_category_id:
            context['sub_category_id'] = int(sub_category_id)
        
        # Get current language from Django's i18n
        from django.utils import translation
        current_language = translation.get_language()
        
        # Map Django language codes to our model language codes
        language_mapping = {
            'en': 'english',
            'ar': 'arabic'
        }
        current_lang = language_mapping.get(current_language, 'english')
        context['current_language'] = current_lang
        
        return context




# Added By me


from .models import Article, ArticleImage

def upload_article(request):
    if request.method == 'POST':
        # Detect the language of the input content
        from .ai_services import AIService
        ai_service = AIService()
        
        title = request.POST.get('title', '')
        short_description = request.POST.get('short_description', '')
        brief_description = request.POST.get('brief_description', '')
        
        # Combine content for language detection
        combined_content = f"{title} {short_description} {brief_description}".strip()
        
        # Auto-detect language from content
        detected_language = 'english'  # Default
        if combined_content:
            try:
                language_result = ai_service.detect_language(combined_content)
                detected_language = language_result.get('language', 'english')
            except Exception as e:
                # Fallback: simple heuristic
                if any('\u0600' <= char <= '\u06FF' for char in combined_content):
                    detected_language = 'arabic'
                else:
                    detected_language = 'english'
        
        # Create the main article in the detected language
        main_article = Article(
            title=title,
            short_description=short_description,
            brief_description=brief_description,
            user=request.user,
            language=detected_language,
            original_language=detected_language,
        )
        
        # Only set category if provided
        category_id = request.POST.get('category')
        if category_id:
            main_article.category_id = category_id
        
        main_article.save()
        
        # Generate translation to the other language
        target_language = 'arabic' if detected_language == 'english' else 'english'
        
        try:
            
            # Translate all content
            translated_title = title
            translated_short_desc = short_description
            translated_brief_desc = brief_description
            
            if title:
                title_translation = ai_service.translate_content(title, detected_language, target_language)
                if 'translated_text' in title_translation:
                    translated_title = title_translation['translated_text']
            
            if short_description:
                short_desc_translation = ai_service.translate_content(short_description, detected_language, target_language)
                if 'translated_text' in short_desc_translation:
                    translated_short_desc = short_desc_translation['translated_text']
            
            if brief_description:
                brief_desc_translation = ai_service.translate_content(brief_description, detected_language, target_language)
                if 'translated_text' in brief_desc_translation:
                    translated_brief_desc = brief_desc_translation['translated_text']
            
            # Create the translated article as a separate record
            translated_article = Article(
                title=translated_title,
                short_description=translated_short_desc,
                brief_description=translated_brief_desc,
                user=request.user,
                language=target_language,
                original_language=detected_language,
                parent_article=main_article,
                ai_translated=True,
                translation_status='translated',
                category=main_article.category,
                subcategory=main_article.subcategory,
                status=main_article.status,
                visibility=main_article.visibility,
            )
            translated_article.save()
            
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Main article is still saved, just without translation

        # Save the uploaded images
        images = request.FILES.getlist('images')  # Get all uploaded images
        for image in images:
            ArticleImage.objects.create(article=main_article, image=image)

        # Add success message about automatic translation
        if 'translated_article' in locals():
            messages.success(request, f'✅ Article created successfully! AI automatically detected {detected_language} and created both English and Arabic versions.')
        else:
            messages.success(request, f'✅ Article created successfully in {detected_language}! (Translation will be processed in background)')
        
        # Render the form.html template with the article and its images
        return render(request, 'form.html', {'article': main_article})

    # Render the form.html template for GET requests
    return render(request, 'form.html')
