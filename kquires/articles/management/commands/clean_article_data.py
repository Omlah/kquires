from django.core.management.base import BaseCommand
from django.db import transaction
import json
import re

class Command(BaseCommand):
    help = 'Clean up article data by extracting clean text from JSON-formatted fields'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        from kquires.articles.models import Article
        
        articles = Article.objects.all()
        cleaned_count = 0
        
        for article in articles:
            changes_made = False
            
            # Clean title
            if article.title and self._is_json_string(article.title):
                original_title = article.title
                article.title = self._extract_clean_text(article.title)
                if article.title != original_title:
                    changes_made = True
                    if dry_run:
                        self.stdout.write(f"Would clean title: '{original_title}' -> '{article.title}'")
            
            # Clean short_description
            if article.short_description and self._is_json_string(article.short_description):
                original_short_desc = article.short_description
                article.short_description = self._extract_clean_text(article.short_description)
                if article.short_description != original_short_desc:
                    changes_made = True
                    if dry_run:
                        self.stdout.write(f"Would clean short_description: '{original_short_desc}' -> '{article.short_description}'")
            
            # Clean brief_description
            if article.brief_description and self._is_json_string(article.brief_description):
                original_brief_desc = article.brief_description
                article.brief_description = self._extract_clean_text(article.brief_description)
                if article.brief_description != original_brief_desc:
                    changes_made = True
                    if dry_run:
                        self.stdout.write(f"Would clean brief_description: '{original_brief_desc[:50]}...' -> '{article.brief_description[:50]}...'")
            
            if changes_made:
                if not dry_run:
                    article.save()
                cleaned_count += 1
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Dry run complete. Would clean {cleaned_count} articles.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully cleaned {cleaned_count} articles.'))

    def _is_json_string(self, text):
        """Check if text looks like a JSON string"""
        if not text or not isinstance(text, str):
            return False
        text = text.strip()
        return text.startswith('{') and text.endswith('}')

    def _extract_clean_text(self, text):
        """Extract clean text from potentially JSON-formatted text"""
        if not text:
            return text
        
        # Check if it's a JSON string
        if self._is_json_string(text):
            try:
                data = json.loads(text)
                # If it's a translation response, extract the translated text
                if isinstance(data, dict) and 'translated_text' in data:
                    return data['translated_text']
                # If it's a translation response, extract the original text
                elif isinstance(data, dict) and 'original_text' in data:
                    return data['original_text']
            except (json.JSONDecodeError, TypeError):
                pass
        
        return text
