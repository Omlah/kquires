from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Log  # Assuming Log is your activity log model

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    Log.objects.create(
        user=user,
        action='login',
        details=f'User {user.name} logged in',
        timestamp=now()  # Optional, if your Log model has a `timestamp` field
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    Log.objects.create(
        user=user,
        action='logout',
        details=f'User {user.name} logged out',
        timestamp=now()  # Optional, if your Log model has a `timestamp` field
    )
