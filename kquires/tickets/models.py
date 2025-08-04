from django.db import models
from ..categories.models import Category
from ..users.models import User
from datetime import datetime

# Create your models here.
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='User', related_name='tickets', null=True, blank=True, default=None)
    title = models.CharField(blank=True, max_length=255, verbose_name='Title')
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Category')
    description = models.TextField(blank=True,verbose_name='Description')
    status = models.CharField(default='pending' ,blank=True, max_length=255, verbose_name='Status')
    created_at = models.DateTimeField(default=datetime.now, blank=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

