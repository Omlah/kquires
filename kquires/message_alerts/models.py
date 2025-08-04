from django.db import models
from datetime import datetime

# Create your models here.
class MessageAlert(models.Model):
    message = models.CharField(blank=True, max_length=2000)
    visibility = models.BooleanField(default=0 ,blank=True, max_length=10, verbose_name='Visibility')
    created_at = models.DateTimeField(default=datetime.now, blank=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, blank=True, verbose_name="Updated At")
