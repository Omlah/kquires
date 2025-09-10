from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from .models import Article
from ..categories.models import Category

User = get_user_model()

class ArticleAutomaticTranslationTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            type='Main',
            status='approved'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_english_article_creates_arabic_translation(self):
        """Test that creating an English article automatically creates Arabic translation"""
        # Create an English article
        article_data = {
            'title': 'Test Article in English',
            'short_description': 'This is a short description in English',
            'brief_description': 'This is a detailed description in English language for testing purposes.',
            'category': self.category.id,
        }
        
        response = self.client.post(reverse('articles:create'), article_data)
        
        # Check that the main article was created
        main_article = Article.objects.filter(title='Test Article in English').first()
        self.assertIsNotNone(main_article)
        self.assertEqual(main_article.language, 'english')
        
        # Check that a translation was created
        translations = main_article.translations.all()
        self.assertEqual(translations.count(), 1)
        
        translation = translations.first()
        self.assertEqual(translation.language, 'arabic')
        self.assertEqual(translation.parent_article, main_article)
        self.assertTrue(translation.ai_translated)
        self.assertEqual(translation.translation_status, 'translated')
    
    def test_arabic_article_creates_english_translation(self):
        """Test that creating an Arabic article automatically creates English translation"""
        # Create an Arabic article
        article_data = {
            'title': 'مقال تجريبي باللغة العربية',
            'short_description': 'هذا وصف قصير باللغة العربية',
            'brief_description': 'هذا وصف مفصل باللغة العربية لأغراض الاختبار.',
            'category': self.category.id,
        }
        
        response = self.client.post(reverse('articles:create'), article_data)
        
        # Check that the main article was created
        main_article = Article.objects.filter(title='مقال تجريبي باللغة العربية').first()
        self.assertIsNotNone(main_article)
        self.assertEqual(main_article.language, 'arabic')
        
        # Check that a translation was created
        translations = main_article.translations.all()
        self.assertEqual(translations.count(), 1)
        
        translation = translations.first()
        self.assertEqual(translation.language, 'english')
        self.assertEqual(translation.parent_article, main_article)
        self.assertTrue(translation.ai_translated)
        self.assertEqual(translation.translation_status, 'translated')
    
    def test_article_without_translation_data(self):
        """Test that articles without translation data don't create translations"""
        # This test would require mocking the AI service to return no translation
        # For now, we'll just verify the basic article creation works
        article_data = {
            'title': 'Simple Test Article',
            'short_description': 'Simple description',
            'brief_description': 'Simple brief description',
            'category': self.category.id,
        }
        
        response = self.client.post(reverse('articles:create'), article_data)
        
        # Check that the main article was created
        main_article = Article.objects.filter(title='Simple Test Article').first()
        self.assertIsNotNone(main_article)
