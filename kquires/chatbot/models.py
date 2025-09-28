from django.db import models
from django.contrib.auth import get_user_model
from kquires.articles.models import Article
from django.utils import timezone

User = get_user_model()


class ChatSession(models.Model):
    """Model to track chat sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Role-based fields
    user_role = models.CharField(max_length=100, blank=True, verbose_name="User Role")
    department = models.ForeignKey('departments.Department', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat Session {self.session_id} - {self.user.name}"
    
    def get_user_primary_role(self):
        """Determine the user's primary role"""
        user = self.user
        if user.is_admin:
            return 'admin'
        elif user.is_approval_manager:
            return 'approval_manager'
        elif user.is_article_writer:
            return 'article_writer'
        elif user.is_manager:
            return 'manager'
        elif user.is_employee:
            return 'employee'
        return 'employee'  # default
    
    def save(self, *args, **kwargs):
        if self.user and not self.user_role:
            self.user_role = self.get_user_primary_role()
            self.department = self.user.department
        super().save(*args, **kwargs)


class ChatMessage(models.Model):
    """Model to store chat messages"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # For bot responses, store referenced articles
    referenced_articles = models.ManyToManyField(Article, blank=True, related_name='chat_references')
    
    # Store AI analysis metadata
    ai_analysis = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."


class ChatbotKnowledge(models.Model):
    """Model to store chatbot knowledge base entries"""
    title = models.CharField(max_length=255)
    content = models.TextField()
    keywords = models.JSONField(default=list, help_text="List of keywords for matching")
    category = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title