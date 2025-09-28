#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/mac/Desktop/Owned/owned/kquires')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from kquires.articles.models import Article
from kquires.users.models import User
from kquires.chatbot.role_based_service import RoleBasedArticleService

def test_article_search():
    print("🔍 Testing Article Search Functionality")
    print("=" * 50)
    
    # Check total articles
    total_articles = Article.objects.count()
    print(f"📚 Total articles in database: {total_articles}")
    
    if total_articles == 0:
        print("❌ No articles found in database!")
        return
    
    # Check approved and visible articles
    approved_articles = Article.objects.filter(status='approved').count()
    visible_articles = Article.objects.filter(visibility=True).count()
    approved_and_visible = Article.objects.filter(status='approved', visibility=True).count()
    
    print(f"✅ Approved articles: {approved_articles}")
    print(f"👁️  Visible articles: {visible_articles}")
    print(f"✅ Approved AND visible: {approved_and_visible}")
    
    # Show sample articles
    print("\n📄 Sample articles:")
    for article in Article.objects.all()[:5]:
        print(f"  - {article.title}")
        print(f"    Status: {article.status}, Visible: {article.visibility}")
        print(f"    Category: {article.category.name if article.category else 'None'}")
        print(f"    User: {article.user.email if article.user else 'None'}")
        print("")
    
    # Test search queries
    print("🔍 Testing search queries:")
    test_queries = ['test', 'guide', 'admin', 'user', 'system']
    
    for query in test_queries:
        results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(brief_description__icontains=query)
        ).filter(status='approved', visibility=True)
        
        print(f"  Query '{query}': {results.count()} results")
        for result in results[:2]:
            print(f"    - {result.title}")
    
    # Test role-based search
    print("\n👤 Testing role-based search:")
    users = User.objects.all()
    if users.exists():
        user = users.first()
        print(f"Testing with user: {user.email}")
        
        role_service = RoleBasedArticleService(user)
        
        accessible = role_service.get_accessible_articles()
        print(f"Accessible articles for {role_service.user_role}: {accessible.count()}")
        
        for query in ['test', 'guide']:
            results = role_service.search_role_specific_articles(query)
            print(f"  Role-based search '{query}': {results.count()} results")
    
    # Test intent detection
    print("\n🎯 Testing intent detection:")
    test_messages = [
        "just give me the articles whose title test",
        "find articles about testing",
        "show me guides",
        "what is the weather today",
        "search for admin articles"
    ]
    
    for message in test_messages:
        intent = role_service.detect_article_search_intent(message)
        terms = role_service.extract_search_terms(message)
        print(f"  '{message}' -> Intent: {intent}, Terms: {terms}")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_article_search()
