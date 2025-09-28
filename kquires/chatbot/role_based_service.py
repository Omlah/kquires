from django.db.models import Q
from kquires.articles.models import Article
from kquires.users.models import User


class RoleBasedArticleService:
    """Service to filter articles based on user roles and permissions"""
    
    def __init__(self, user):
        self.user = user
        self.user_role = self.get_user_primary_role()
        self.department = user.department
    
    def get_user_primary_role(self):
        """Determine user's primary role"""
        if self.user.is_admin:
            return 'admin'
        elif self.user.is_approval_manager:
            return 'approval_manager'
        elif self.user.is_article_writer:
            return 'article_writer'
        elif self.user.is_manager:
            return 'manager'
        elif self.user.is_employee:
            return 'employee'
        return 'employee'
    
    def get_user_role_display(self):
        """Get user-friendly role name"""
        role_names = {
            'admin': 'Administrator',
            'approval_manager': 'Approval Manager',
            'article_writer': 'Article Writer',
            'manager': 'Manager',
            'employee': 'Employee'
        }
        return role_names.get(self.user_role, 'Employee')
    
    def search_role_specific_articles(self, query):
        """Search articles with direct database query - no fetching all articles"""
        print(f"🔍 Direct search for '{query}'")
        
        # Single optimized query - search and filter in one go
        search_results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(brief_description__icontains=query) |
            Q(category__name__icontains=query),
            status='approved'  # Only approved articles
        ).distinct()[:10]
        
        print(f"🔍 Search results: {search_results.count()} articles found")
        
        # Debug: Show what articles were found
        for article in search_results:
            print(f"   - {article.title} (Status: {article.status})")
        
        return search_results
    
    def detect_article_search_intent(self, user_message):
        """Detect if user wants to find articles"""
        search_keywords = [
            'find', 'search', 'show', 'get', 'give', 'list', 'articles', 'article',
            'documentation', 'docs', 'guide', 'help', 'information', 'content'
        ]
        
        user_message_lower = user_message.lower()
        
        # Check for article search intent
        for keyword in search_keywords:
            if keyword in user_message_lower:
                return True
        
        # Check for specific patterns
        patterns = [
            'articles about', 'articles with', 'articles containing',
            'find articles', 'search articles', 'show articles',
            'give me articles', 'list articles'
        ]
        
        for pattern in patterns:
            if pattern in user_message_lower:
                return True
        
        return False
    
    def extract_search_terms(self, user_message):
        """Extract search terms from user message - optimized for database queries"""
        # Remove common words and extract meaningful terms
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'articles', 'article', 'find', 'search', 'show', 'get', 'give', 'list']
        
        words = user_message.lower().split()
        search_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # If no meaningful terms found, use the original message
        if not search_terms:
            search_terms = [user_message.strip()]
        
        # Return the first meaningful term for database query
        return search_terms[0] if search_terms else user_message.strip()
    
    def get_role_specific_suggestions(self):
        """Get quick action suggestions based on user role"""
        suggestions = {
            'admin': [
                "Show me system administration articles",
                "User management guides",
                "System configuration help",
                "Security policies"
            ],
            'approval_manager': [
                "Articles pending approval",
                "Content review guidelines",
                "Approval workflow help",
                "Quality standards"
            ],
            'article_writer': [
                "Writing guidelines",
                "Content creation best practices",
                "My draft articles",
                "Publishing workflow"
            ],
            'manager': [
                "Team management resources",
                "Department procedures",
                "Performance guidelines",
                "Leadership resources"
            ],
            'employee': [
                "Getting started guide",
                "Common procedures",
                "Department resources",
                "FAQ"
            ]
        }
        return suggestions.get(self.user_role, suggestions['employee'])
    
    def get_popular_articles_for_role(self, limit=5):
        """Get popular articles based on user role"""
        accessible_articles = self.get_accessible_articles()
        return accessible_articles.order_by('-click_count')[:limit]
    
    def get_recent_articles_for_role(self, limit=5):
        """Get recent articles based on user role"""
        accessible_articles = self.get_accessible_articles()
        return accessible_articles.order_by('-created_at')[:limit]
