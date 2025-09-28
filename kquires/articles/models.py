from django.db import models
from ..categories.models import Category
from ..users.models import User
from datetime import datetime
import json


class Article(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('draft', 'Draft'),
        ('ai_generated', 'AI Generated'),
    ]
    
    LANGUAGE_CHOICES = [
        ('english', 'English'),
        ('arabic', 'Arabic'),
    ]
    
    title = models.CharField(blank=True, max_length=255, verbose_name='Title')
    attachment = models.FileField(upload_to='attachments/', verbose_name='Attachment', null=True, blank=True)
    
    # Google Drive integration fields
    google_drive_file_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='Google Drive File ID')
    google_drive_filename = models.CharField(max_length=255, blank=True, null=True, verbose_name='Google Drive Filename')
    google_drive_web_view_link = models.URLField(blank=True, null=True, verbose_name='Google Drive Web View Link')
    google_drive_web_content_link = models.URLField(blank=True, null=True, verbose_name='Google Drive Web Content Link')
    google_drive_file_size = models.BigIntegerField(blank=True, null=True, verbose_name='Google Drive File Size')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Category', related_name='articles')
    subcategory = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        verbose_name='Subcategory', 
        related_name='subcategory_articles', 
        null=True, 
        blank=True
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        verbose_name='User', 
        related_name='articles', 
        null=True, 
        blank=True, 
        default=None
    )
    short_description = models.CharField(max_length=255, verbose_name='Short Description', null=True, blank=True)
    brief_description = models.TextField(verbose_name='Brief Description', null=True, blank=True)
    status = models.CharField(default='pending', choices=STATUS_CHOICES, max_length=255, verbose_name='Status')
    comment = models.CharField(default='', blank=True, max_length=255, verbose_name='Comment')
    visibility = models.BooleanField(default=False, blank=True, verbose_name='Visibility')
    created_at = models.DateTimeField(default=datetime.now, blank=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    click_count = models.PositiveIntegerField(default=0, verbose_name="Click Count")
    
    # AI Enhancement Fields
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='english', verbose_name='Language')
    original_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, null=True, blank=True, verbose_name='Original Language')
    ai_analysis = models.JSONField(null=True, blank=True, verbose_name='AI Analysis')
    technical_terms = models.JSONField(null=True, blank=True, verbose_name='Technical Terms')
    version = models.CharField(max_length=10, default='1.0', verbose_name='Version')
    is_ai_generated = models.BooleanField(default=False, verbose_name='AI Generated')
    requires_approval = models.BooleanField(default=False, verbose_name='Requires Approval')
    translation_preview = models.TextField(null=True, blank=True, verbose_name='Translation Preview')
    parent_article = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='translations', 
        verbose_name='Parent Article'
    )
    
    # Translation Status
    TRANSLATION_STATUS_CHOICES = [
        ('not_translated', 'Not Translated'),
        ('pending', 'Pending Translation'),
        ('translated', 'Translated'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    translation_status = models.CharField(
        max_length=20, 
        choices=TRANSLATION_STATUS_CHOICES,
        default='not_translated',
        verbose_name='Translation Status'
    )
    
    # AI Translation field
    ai_translated = models.BooleanField(default=False, verbose_name='AI Translated')
    
    # Additional fields for Arabic translations
    title_ar = models.CharField(max_length=255, blank=True, null=True, verbose_name='Title (Arabic)')
    short_description_ar = models.CharField(max_length=255, blank=True, null=True, verbose_name='Short Description (Arabic)')
    brief_description_ar = models.TextField(blank=True, null=True, verbose_name='Brief Description (Arabic)')
    last_translated_at = models.DateTimeField(blank=True, null=True, verbose_name='Last Translated At')
    title_arabic = models.CharField(max_length=255, blank=True, null=True, verbose_name='Title (Arabic)')
    short_description_arabic = models.CharField(max_length=255, blank=True, null=True, verbose_name='Short Description (Arabic)')
    brief_description_arabic = models.TextField(blank=True, null=True, verbose_name='Brief Description (Arabic)')
    manually_edited = models.BooleanField(default=False, verbose_name='Manually Edited')
    
    def __str__(self):
        return self.title
    
    def _extract_clean_text(self, text):
        """Extract clean text from potentially JSON-formatted text"""
        if not text:
            return text
        if isinstance(text, str) and text.strip().startswith('{') and text.strip().endswith('}'):
            try:
                data = json.loads(text)
                if isinstance(data, dict) and 'translated_text' in data:
                    return data['translated_text']
                elif isinstance(data, dict) and 'original_text' in data:
                    return data['original_text']
            except (json.JSONDecodeError, TypeError):
                pass
        return text
    
    def record_click(self):
        """Increments the click count every time the article is viewed."""
        self.click_count += 1
        self.save(update_fields=['click_count'])
    
    def get_translations(self):
        """Get all translations of this article"""
        if self.parent_article:
            return self.parent_article.translations.all()
        return self.translations.all()
    
    def get_available_languages(self):
        """Get list of available languages for this article"""
        languages = [self.language]
        if self.parent_article:
            languages.append(self.parent_article.language)
            languages.extend([t.language for t in self.parent_article.translations.all()])
        else:
            languages.extend([t.language for t in self.translations.all()])
        return list(set(languages))
    
    def get_title_for_language(self, target_language):
        """Get title in the specified language"""
        if self.language == target_language:
            return self._extract_clean_text(self.title)
        translation = self.parent_article.translations.filter(language=target_language).first() if self.parent_article else self.translations.filter(language=target_language).first()
        return self._extract_clean_text(translation.title) if translation else self._extract_clean_text(self.title)
    
    def get_short_description_for_language(self, target_language):
        """Get short description in the specified language"""
        if self.language == target_language:
            return self._extract_clean_text(self.short_description)
        translation = self.parent_article.translations.filter(language=target_language).first() if self.parent_article else self.translations.filter(language=target_language).first()
        return self._extract_clean_text(translation.short_description) if translation else self._extract_clean_text(self.short_description)
    
    def get_brief_description_for_language(self, target_language):
        """Get brief description in the specified language"""
        if self.language == target_language:
            return self._extract_clean_text(self.brief_description)
        translation = self.parent_article.translations.filter(language=target_language).first() if self.parent_article else self.translations.filter(language=target_language).first()
        return self._extract_clean_text(translation.brief_description) if translation else self._extract_clean_text(self.brief_description)
    
    def has_translation(self, target_language):
        """Check if translation exists for the specified language"""
        if self.language == target_language:
            return True
        if self.parent_article:
            return self.parent_article.translations.filter(language=target_language).exists()
        return self.translations.filter(language=target_language).exists()
    
    def create_translation(self, target_language, translated_content, user=None):
        """Create a translation of this article"""
        technical_terms = self.technical_terms or []
        translation = Article.objects.create(
            title=f"{self.title} ({target_language.title()})",
            brief_description=translated_content,
            category=self.category,
            subcategory=self.subcategory,
            user=user,
            language=target_language,
            original_language=self.language,
            parent_article=self.parent_article or self,
            status='draft',
            is_ai_generated=True,
            requires_approval=True,
            version='1.0',
            technical_terms=technical_terms
        )
        return translation
    
    def validate_category_assignment(self):
        """Validate that article has exactly one main category and one subcategory"""
        errors = []
        if not hasattr(self, 'category_id') or not self.category_id:
            errors.append("Article must have a main category")
        else:
            try:
                if self.category.type != 'Main':
                    errors.append("Main category must be of type 'Main'")
            except:
                pass
        if hasattr(self, 'subcategory_id') and self.subcategory_id:
            try:
                if self.subcategory.type != 'Sub':
                    errors.append("Subcategory must be of type 'Sub'")
                if hasattr(self, 'category_id') and self.category_id and self.subcategory.parent_category_id != self.category_id:
                    errors.append("Subcategory must belong to the selected main category")
            except:
                pass
        return errors
    
    def upload_to_google_drive(self, file_content, filename, mime_type=None):
        """
        Upload file to Google Drive and update article fields
        
        Args:
            file_content: File content as bytes
            filename: Name of the file
            mime_type: MIME type of the file
            
        Returns:
            Dict containing upload result
        """
        try:
            from ..utils.google_drive_service import google_drive_service
            
            # Upload to Google Drive
            result = google_drive_service.upload_file(
                file_content=file_content,
                filename=filename,
                mime_type=mime_type
            )
            
            if result.get('success'):
                # Update article fields with Google Drive information
                self.google_drive_file_id = result.get('file_id')
                self.google_drive_filename = result.get('filename')
                self.google_drive_web_view_link = result.get('web_view_link')
                self.google_drive_web_content_link = result.get('web_content_link')
                self.google_drive_file_size = result.get('size')
                self.save(update_fields=[
                    'google_drive_file_id',
                    'google_drive_filename', 
                    'google_drive_web_view_link',
                    'google_drive_web_content_link',
                    'google_drive_file_size'
                ])
            
            return result
            
        except Exception as e:
            return {'error': f'Failed to upload to Google Drive: {str(e)}'}
    
    def delete_from_google_drive(self):
        """
        Delete file from Google Drive
        
        Returns:
            Dict containing deletion result
        """
        try:
            if not self.google_drive_file_id:
                return {'error': 'No Google Drive file ID found'}
            
            from ..utils.google_drive_service import google_drive_service
            
            result = google_drive_service.delete_file(self.google_drive_file_id)
            
            if result.get('success'):
                # Clear Google Drive fields
                self.google_drive_file_id = None
                self.google_drive_filename = None
                self.google_drive_web_view_link = None
                self.google_drive_web_content_link = None
                self.google_drive_file_size = None
                self.save(update_fields=[
                    'google_drive_file_id',
                    'google_drive_filename',
                    'google_drive_web_view_link', 
                    'google_drive_web_content_link',
                    'google_drive_file_size'
                ])
            
            return result
            
        except Exception as e:
            return {'error': f'Failed to delete from Google Drive: {str(e)}'}
    
    def get_google_drive_file_info(self):
        """
        Get current Google Drive file information
        
        Returns:
            Dict containing file information
        """
        try:
            if not self.google_drive_file_id:
                return {'error': 'No Google Drive file ID found'}
            
            from ..utils.google_drive_service import google_drive_service
            return google_drive_service.get_file_info(self.google_drive_file_id)
            
        except Exception as e:
            return {'error': f'Failed to get Google Drive file info: {str(e)}'}
    
    def has_google_drive_file(self):
        """Check if article has a Google Drive file"""
        return bool(self.google_drive_file_id)
    
    def save(self, *args, **kwargs):
        """Override save to validate category assignment"""
        if hasattr(self, 'category_id') and self.category_id:
            errors = self.validate_category_assignment()
            if errors:
                raise ValueError(f"Category validation failed: {'; '.join(errors)}")
        super().save(*args, **kwargs)


class ArticleVersion(models.Model):
    """Model to track article versions for version control"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=10, verbose_name='Version Number')
    title = models.CharField(max_length=255, verbose_name='Title')
    content = models.TextField(verbose_name='Content')
    language = models.CharField(max_length=20, choices=Article.LANGUAGE_CHOICES, verbose_name='Language')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Created By')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    change_summary = models.TextField(null=True, blank=True, verbose_name='Change Summary')
    is_current = models.BooleanField(default=False, verbose_name='Is Current Version')
    
    class Meta:
        unique_together = ['article', 'version_number']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.article.title} v{self.version_number}"


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='article_images/', verbose_name='Image')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Uploaded At')
    
    def __str__(self):
        return f"Image for {self.article.title}"
