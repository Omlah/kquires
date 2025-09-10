"""
API views for article translation operations
"""

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Article
from .ai_services import ai_service
import json


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def translate_article_view(request, article_id):
    """Translate an article to the target language"""
    try:
        article = get_object_or_404(Article, id=article_id)
        data = json.loads(request.body)
        target_language = data.get('target_language')
        
        if not target_language:
            return JsonResponse({'error': 'Target language is required'}, status=400)
        
        # Check if translation already exists
        existing_translation = article.translations.filter(language=target_language).first()
        if existing_translation:
            return JsonResponse({
                'message': 'Translation already exists',
                'translation_id': existing_translation.id
            })
        
        # Get the main article (parent or self)
        main_article = article.parent_article if article.parent_article else article
        
        # Detect language of the main article
        combined_content = f"{main_article.title} {main_article.short_description} {main_article.brief_description}"
        detected_language = ai_service.detect_language(combined_content)
        
        # Translate content
        title_translation = ai_service.translate_content(main_article.title, detected_language, target_language)
        short_desc_translation = ai_service.translate_content(main_article.short_description, detected_language, target_language)
        brief_desc_translation = ai_service.translate_content(main_article.brief_description, detected_language, target_language)
        
        # Extract translated text from responses
        translated_title = title_translation.get('translated_text', main_article.title) if isinstance(title_translation, dict) else main_article.title
        translated_short_desc = short_desc_translation.get('translated_text', main_article.short_description) if isinstance(short_desc_translation, dict) else main_article.short_description
        translated_brief_desc = brief_desc_translation.get('translated_text', main_article.brief_description) if isinstance(brief_desc_translation, dict) else main_article.brief_description
        
        # Create translation
        translated_article = Article(
            title=translated_title,
            short_description=translated_short_desc,
            brief_description=translated_brief_desc,
            user=main_article.user,
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
        
        return JsonResponse({
            'message': 'Translation completed successfully',
            'translation_id': translated_article.id,
            'translation_preview': {
                'title': translated_title,
                'short_description': translated_short_desc,
                'brief_description': translated_brief_desc
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_task_status(request, task_id):
    """Get the status of a background task"""
    # For now, return a simple success status since we're doing synchronous translation
    return JsonResponse({
        'status': 'SUCCESS',
        'result': 'Translation completed'
    })
