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
        query = Article.objects.order_by('-updated_at').all()
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
        if article_id:
            self.object = get_object_or_404(Article, id=article_id)  # ✅ Assign `self.object`
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
            self.object.save()
            user = User.objects.get(id=self.request.user.id)
            user.log(action, f"Article successfully {action}.")
            messages.success(request, f"Article successfully {action}.")
            return self.form_valid(form)  # ✅ Call `form_valid()`
        else:
            return self.form_invalid(form)

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
    return JsonResponse({
        'id': article.id,
        'title': article.title,
        # 'attachment': article.attachment,
        'category': article.category.name,
        'short_description': article.short_description,
        'brief_description': article.brief_description,
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
        query = Article.objects.filter( status='approved')
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
        return context




# Added By me


from .models import Article, ArticleImage

def upload_article(request):
    if request.method == 'POST':
        # Save the article
        article = Article(
            title=request.POST.get('title'),
            short_description=request.POST.get('short_description'),
            brief_description=request.POST.get('brief_description'),
            user=request.user,  # Assuming the user is authenticated
            category_id=request.POST.get('category'),  # Assuming category is passed as an ID
        )
        article.save()

        # Save the uploaded images
        images = request.FILES.getlist('images')  # Get all uploaded images
        for image in images:
            ArticleImage.objects.create(article=article, image=image)

        # Render the form.html template with the article and its images
        return render(request, 'form.html', {'article': article})

    # Render the form.html template for GET requests
    return render(request, 'form.html')
