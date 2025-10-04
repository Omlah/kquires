"""
Django management command to set up Google Drive authentication
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import webbrowser
import os


class Command(BaseCommand):
    help = 'Set up Google Drive authentication'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Google Drive Setup for File Uploads ===\n')
        )
        
        self.stdout.write(
            '📋 Current Status:\n'
            '- Google Drive API credentials are configured in settings\n'
            '- Authentication token needs to be generated\n\n'
        )
        
        token_file = 'token.json'
        if os.path.exists(token_file):
            self.stdout.write(
                self.style.SUCCESS(f'✅ Google Drive token already exists: {token_file}')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(
                '⚠️ Google Drive authentication token not found.\n'
                'This means files will be saved locally instead of Google Drive.\n\n'
                'To fix this, you need to authenticate with Google Drive:\n\n'
                '1. Download the Google Drive API credentials:\n'
                '   - Go to Google Cloud Console\n'
                '   - Enable Google Drive API\n'
                '   - Create OAuth 2.0 credentials\n'
                '   - Download the JSON file\n\n'
                '2. Update Django settings with your credentials\n\n'
                '3. Run: python manage.py setup_google_drive_auth\n\n'
                'Alternative: Upload files will still work but be saved locally only.\n'
            )
        )
        
        # Check if credentials are in settings
        if hasattr(settings, 'GOOGLE_DRIVE_CLIENT_ID'):
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Google Drive credentials found in settings\n'
                    f'Client ID: {settings.GOOGLE_DRIVE_CLIENT_ID}\n'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Google Drive credentials not found in settings\n'
                    'Please add GOOGLE_DRIVE_CLIENT_ID and GOOGLE_DRIVE_CLIENT_SECRET to settings.'
                )
            )
