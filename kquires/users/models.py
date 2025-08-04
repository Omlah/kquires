from typing import ClassVar
from django.contrib.auth.models import AbstractUser
from django.db.models import SET_NULL, ForeignKey, CharField, EmailField, DateField, DateTimeField, BooleanField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from ..departments.models import Department

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for kquires.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """ 

    username = None  # Remove the username field
    employee_id = CharField(unique=True, blank=True, null=True, max_length=255)
    name = CharField(blank=True, max_length=255) 
    email = EmailField(unique=True)
    phone_number = CharField(blank=True, max_length=50, verbose_name="Phone Number")
    mobile_number = CharField(blank=True, max_length=15, verbose_name="Mobile Number")
    job_title = CharField(blank=True, max_length=100, verbose_name="Job Title")
    email_enabled = CharField(blank=True, max_length=100, verbose_name="Email Enabled")
    registration_date = DateField(blank=True, null=True, verbose_name="Registration Date")
    department = ForeignKey(Department, on_delete=SET_NULL, verbose_name='Department', related_name='users', null=True, blank=True, default=None)
    role = CharField(blank=True, max_length=100, verbose_name="Role")
    status = CharField(blank=True, max_length=100, verbose_name="Status")
    is_admin = BooleanField(default=False, verbose_name="Is Admin")
    is_article_writer = BooleanField(default=False, verbose_name="Is Article Writer")
    is_approval_manager = BooleanField(default=False, verbose_name="Is Approval Manager")
    is_manager = BooleanField(default=False, verbose_name="Is Manager")
    is_employee = BooleanField(default=False, verbose_name="Is Employee")
    created_at = DateTimeField(default=datetime.now, blank=True, verbose_name="Created At") 
    updated_at = DateTimeField(auto_now=True, verbose_name="Updated At")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str: 
        """Get URL for user's detail view."""
        return reverse("users:detail", kwargs={"pk": self.id})
    
    def log(self, action: str, details: str = "") -> None:
        from ..logs.models import Log 
        Log.objects.create(user=self, action=action, details=details)
