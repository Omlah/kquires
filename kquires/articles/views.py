from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, View
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import strip_tags
from django.utils.translation import get_language
from .models import Article
from .forms import ArticleForm
from ..notifications.models import Notification
from ..utils.translation_service import detect_language, translate_text, clean_ai_json


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
