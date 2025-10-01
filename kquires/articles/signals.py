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
                # Only create notification if user exists
                if instance.user:
                    Notification.objects.create(user=instance.user, article=instance, message=message)


@receiver(post_save, sender=Article)
def create_automatic_translation(sender, instance, created, **kwargs):
    """Create automatic translation after main article is saved"""
    if created and hasattr(instance, '_translation_data'):
        try:
            translation_data = instance._translation_data

            # Create the translated article as a separate record
            translated_article = Article(
                title=translation_data['translated_title'],
                short_description=translation_data['translated_short_desc'],
                brief_description=translation_data['translated_brief_desc'],
                user=instance.user,
                language=translation_data['target_language'],
                original_language=translation_data['detected_language'],
                parent_article=instance,
                ai_translated=True,
                translation_status='translated',
                category=instance.category,
                subcategory=instance.subcategory,
                status=instance.status,
                visibility=instance.visibility,
            )
            translated_article.save()

            # Clean up the temporary data
            delattr(instance, '_translation_data')

        except Exception:
            import traceback
            traceback.print_exc()
            # Continue even if translation fails
