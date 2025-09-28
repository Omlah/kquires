from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
import uuid
import json

from .models import ChatSession, ChatMessage, ChatbotKnowledge
from .ai_service import ChatbotAIService
from .role_based_service import RoleBasedArticleService


class ChatbotView(LoginRequiredMixin, TemplateView):
    """Main chatbot interface view"""
    template_name = 'chatbot/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create a chat session for the user
        session_id = self.request.session.get('chat_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            self.request.session['chat_session_id'] = session_id
        
        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={'user': self.request.user}
        )
        
        # Get recent messages
        recent_messages = session.messages.all()[:20]
        
        context.update({
            'session': session,
            'recent_messages': recent_messages,
        })
        
        return context


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """API endpoint to send a message to the chatbot"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create chat session
        session_id = request.session.get('chat_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['chat_session_id'] = session_id
        
        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={'user': request.user}
        )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message_content
        )
        
        # Process message with AI
        ai_service = ChatbotAIService()
        ai_response = ai_service.process_user_message(message_content)
        
        # Save bot response
        bot_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=ai_response['response'],
            ai_analysis=ai_response['ai_analysis']
        )
        
        # Add referenced articles
        if ai_response['referenced_articles']:
            bot_message.referenced_articles.set(ai_response['referenced_articles'])
        
        # Update session timestamp
        session.updated_at = timezone.now()
        session.save()
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'timestamp': user_message.created_at.isoformat(),
                'type': 'user'
            },
            'bot_response': {
                'id': bot_message.id,
                'content': bot_message.content,
                'timestamp': bot_message.created_at.isoformat(),
                'type': 'bot',
                'referenced_articles': [
                    {
                        'id': article.id,
                        'title': article.title,
                        'url': f'/articles/{article.id}/'
                    }
                    for article in ai_response['referenced_articles']
                ]
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_chat_history(request, session_id):
    """Get chat history for a specific session"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        session = get_object_or_404(ChatSession, session_id=session_id, user=request.user)
        messages = session.messages.all()
        
        message_list = []
        for message in messages:
            message_data = {
                'id': message.id,
                'content': message.content,
                'type': message.message_type,
                'timestamp': message.created_at.isoformat(),
            }
            
            if message.message_type == 'bot' and message.referenced_articles.exists():
                message_data['referenced_articles'] = [
                    {
                        'id': article.id,
                        'title': article.title,
                        'url': f'/articles/{article.id}/'
                    }
                    for article in message.referenced_articles.all()
                ]
            
            message_list.append(message_data)
        
        return JsonResponse({
            'success': True,
            'messages': message_list
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def clear_chat_history(request):
    """Clear chat history for current session"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        session_id = request.session.get('chat_session_id')
        if session_id:
            ChatSession.objects.filter(session_id=session_id, user=request.user).delete()
            del request.session['chat_session_id']
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_role_based_message(request):
    """Enhanced message endpoint with role-based article filtering"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create chat session with role context
        session_id = request.session.get('chat_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['chat_session_id'] = session_id
        
        # Get user's primary role
        role_service = RoleBasedArticleService(request.user)
        user_role = role_service.user_role
        
        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user': request.user,
            }
        )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message_content
        )
        
        # Check if user wants to find articles
        is_article_search = role_service.detect_article_search_intent(message_content)
        
        if is_article_search:
            # Extract search term and search for articles
            search_query = role_service.extract_search_terms(message_content)
            print(f"🔍 Article search detected!")
            print(f"   Search query: '{search_query}'")
            print(f"   User role: {user_role}")
            
            # Direct database query with single search term
            relevant_articles = role_service.search_role_specific_articles(search_query)
            
            print(f"   Total articles found: {len(relevant_articles)}")
            
            # Generate response focused on articles
            ai_response = {
                "response": f"I found {len(relevant_articles)} article(s) related to your search. Here are the results:",
                "ai_analysis": {"article_search": True, "search_query": search_query}
            }
        else:
            # Regular AI response for general questions
            relevant_articles = role_service.search_role_specific_articles(message_content)
            ai_service = ChatbotAIService()
            ai_response = ai_service.generate_response(
                message_content, 
                relevant_articles
            )
        
        # Save bot response
        bot_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=ai_response['response'],
            ai_analysis=ai_response['ai_analysis']
        )
        
        if relevant_articles:
            bot_message.referenced_articles.set(relevant_articles)
        
        # Update session timestamp
        session.updated_at = timezone.now()
        session.save()
        
        # Prepare response
        article_data = []
        for article in relevant_articles:
            article_data.append({
                'id': article.id,
                'title': article.title,
                'url': f'/articles/{article.id}/',
                'short_description': article.short_description
            })
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'timestamp': user_message.created_at.isoformat(),
                'type': 'user'
            },
            'bot_response': {
                'id': bot_message.id,
                'content': bot_message.content,
                'timestamp': bot_message.created_at.isoformat(),
                'type': 'bot',
                'referenced_articles': article_data
            },
            'user_role': user_role
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_role_suggestions(request):
    """Get role-specific quick suggestions"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        role_service = RoleBasedArticleService(request.user)
        suggestions = role_service.get_role_specific_suggestions()
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions,
            'user_role': role_service.user_role,
            'user_role_display': role_service.get_user_role_display()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_role_articles(request):
    """Get articles accessible to the user based on their role"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        role_service = RoleBasedArticleService(request.user)
        
        # Get different types of articles
        popular_articles = role_service.get_popular_articles_for_role(5)
        recent_articles = role_service.get_recent_articles_for_role(5)
        
        def serialize_article(article):
            return {
                'id': article.id,
                'title': article.title,
                'short_description': article.short_description,
                'url': f'/articles/{article.id}/',
                'created_at': article.created_at.isoformat(),
                'click_count': article.click_count
            }
        
        return JsonResponse({
            'success': True,
            'popular_articles': [serialize_article(a) for a in popular_articles],
            'recent_articles': [serialize_article(a) for a in recent_articles],
            'user_role': role_service.user_role,
            'user_role_display': role_service.get_user_role_display()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)