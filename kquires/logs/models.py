from django.db import models
from ..users.models import User

class Log(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='User', related_name='logs', null=True, blank=True, default=None)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}"
