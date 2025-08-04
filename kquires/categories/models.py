from django.db import models
from datetime import datetime
from ..users.models import User
from ..departments.models import Department
# Create your models here.
    
class Category(models.Model):
    
    CATEGORY_TYPE_CHOICES = [
        ('Main', 'Main'),
        ('Sub', 'Sub'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='User', related_name='categories', null=True, blank=True, default=None)
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        verbose_name='Parent Category',
        related_name='subcategories',
        null=True,
        blank=True,
    )
    name = models.CharField(blank=True, max_length=100, verbose_name='Category Name')
    logo = models.ImageField(upload_to='category_logos/', null=True, blank=True, verbose_name="Category Logo")
    type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES,
        default='Main',
    ) 
    departments = models.ManyToManyField(Department, related_name='categories', blank=True)
    subcategory = models.CharField(blank=True, max_length=100, verbose_name='Sub-Category Name')
    category = models.CharField(blank=True, max_length=100, verbose_name='Sub-Category Name')
    status = models.CharField(default='pending' ,blank=True, max_length=255, verbose_name='Status')
    visibility = models.BooleanField(default=0 ,blank=True, max_length=10, verbose_name='Visibility')
    created_at = models.DateTimeField(default=datetime.now, blank=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    comment = models.TextField(null=True, blank=True, verbose_name='Comment')  # Add this line


    def __str__(self):
        return self.name
    
    def get_approved_articles_count(self):
        count = self.articles.filter(status='approved').count()
        
        subcategories = self.subcategories.all()  
        subcategory_articles_count = sum(sub.get_approved_articles_count() for sub in subcategories)

        return count + subcategory_articles_count
    
    def sub_categories(self):
        return Category.objects.filter(status='approved', parent_category=self).order_by('-created_at')[:2]
    def all_sub_categories(self):
        return Category.objects.filter(status='approved', parent_category=self).order_by('-created_at')
    

        