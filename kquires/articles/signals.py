from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from .models import Article
from ..notifications.models import Notification

@receiver(pre_save, sender=Article)
def track_previous_status(sender, instance, **kwargs):

    if instance.pk: 
        try:
            previous_instance = Article.objects.get(pk=instance.pk)
            instance._previous_status = previous_instance.status  
        except Article.DoesNotExist:
            instance._previous_status = None 

@receiver(post_save, sender=Article)
def article_status_update(sender, instance, created, **kwargs):
  
    if not created:  
        previous_status = getattr(instance, '_previous_status', None) 
        if previous_status != instance.status:  
            if instance.status in ['approved', 'rejected']:
              message = f"Your article '{instance.title}' has been {instance.status}."
            Notification.objects.create(user=instance.user, article=instance, message=message)
