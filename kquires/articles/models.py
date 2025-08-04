from django.db import models
from ..categories.models import Category
from ..users.models import User
from datetime import datetime

class Article(models.Model):
    title = models.CharField(blank=True, max_length=255, verbose_name='Title')
    attachment = models.FileField(upload_to='attachments/', verbose_name='Attachment', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Category', related_name='articles')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='User', related_name='articles', null=True, blank=True, default=None)
    short_description = models.CharField(max_length=255, verbose_name='Short Description', null=True, blank=True)
    brief_description = models.TextField(verbose_name='Brief Description', null=True, blank=True)
    status = models.CharField(default='pending', blank=True, max_length=255, verbose_name='Status')
    comment = models.CharField(default='', blank=True, max_length=255, verbose_name='Comment')
    visibility = models.BooleanField(default=False, blank=True, verbose_name='Visibility')
    created_at = models.DateTimeField(default=datetime.now, blank=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    click_count = models.PositiveIntegerField(default=0, verbose_name="Click Count")
    
    def __str__(self):
        return self.title
    
    def record_click(self):
        """Increments the click count every time the article is viewed."""
        self.click_count += 1
        self.save(update_fields=['click_count'])


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='article_images/', verbose_name='Image')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Uploaded At')
    
    def __str__(self):
        return f"Image for {self.article.title}"
    
