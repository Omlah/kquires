"""Management command to clean up articles with JSON data in text fields"""

from django.core.management.base import BaseCommand
from django.db import transaction
from articles.models import Article
import json


class Command(BaseCommand):
    help = 'Clean up articles that have JSON data stored in their text fields'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        articles_to_clean = []
        
        # Find articles with JSON data in their fields
        for article in Article.objects.all():
            needs_cleaning = False
            cleaned_data = {}
            
            # Check title
            if self._is_json_data(article.title):
                cleaned_data['title'] = self._extract_clean_text(article.title)
                needs_cleaning = True
                self.stdout.write(f"Article {article.id}: Title needs cleaning")
            
            # Check short_description
            if self._is_json_data(article.short_description):
                cleaned_data['short_description'] = self._extract_clean_text(article.short_description)
                needs_cleaning = True
                self.stdout.write(f"Article {article.id}: Short description needs cleaning")
            
            # Check brief_description
            if self._is_json_data(article.brief_description):
                cleaned_data['brief_description'] = self._extract_clean_text(article.brief_description)
                needs_cleaning = True
                self.stdout.write(f"Article {article.id}: Brief description needs cleaning")
            
            if needs_cleaning:
                articles_to_clean.append((article, cleaned_data))
        
        if not articles_to_clean:
            self.stdout.write(self.style.SUCCESS('No articles need cleaning!'))
            return
        
        self.stdout.write(f"Found {len(articles_to_clean)} articles that need cleaning")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Would clean the following articles:'))
            for article, cleaned_data in articles_to_clean:
                self.stdout.write(f"  Article {article.id}: {list(cleaned_data.keys())}")
            return
        
        # Clean the articles
        cleaned_count = 0
        with transaction.atomic():
            for article, cleaned_data in articles_to_clean:
                try:
                    for field, value in cleaned_data.items():
                        setattr(article, field, value)
                    article.save()
                    cleaned_count += 1
                    self.stdout.write(f"✅ Cleaned article {article.id}")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Failed to clean article {article.id}: {e}")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleaned {cleaned_count} articles')
        )

    def _is_json_data(self, text):
        """Check if text looks like JSON data"""
        if not text or not isinstance(text, str):
            return False
        text = text.strip()
        return text.startswith('{') and text.endswith('}')

    def _extract_clean_text(self, text):
        """Extract clean text from JSON data"""
        if not text:
            return text
        
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                # If it's a translation response, extract the translated text
                if 'translated_text' in data:
                    return data['translated_text']
                # If it's a translation response, extract the original text
                elif 'original_text' in data:
                    return data['original_text']
        except (json.JSONDecodeError, TypeError):
            pass
        
        return text
