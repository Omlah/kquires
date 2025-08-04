from django.db import models
from datetime import datetime
from ..users.models import User
from ..articles.models import Article

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.CharField(blank=True, max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now, blank=True, verbose_name="Created At")

    def __str__(self):
        return self.message
