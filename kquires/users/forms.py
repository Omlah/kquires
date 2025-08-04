from allauth.account.forms import SignupForm, LoginForm, BaseSignupForm
from allauth.account.adapter import get_adapter
from allauth.account.utils import (
    user_email,
    user_username,
)
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import User
from . import app_settings
from allauth.utils import  set_form_field_order
from django.contrib.auth import (
    REDIRECT_FIELD_NAME,
    get_user_model,
    password_validation,
)
from allauth.account.forms import SignupForm





class CustomLoginForm(LoginForm):
    login = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Enter email or employee ID", "class": "form-control"}),
        label="Email or Employee ID"
    )

    def clean_login(self):
        """
        Override validation to allow both email and employee ID.
        """
        login_input = self.cleaned_data["login"]

        # Check if input is an email or employee_id
        if '@' in login_input:
            if not User.objects.filter(email=login_input).exists():
                raise forms.ValidationError("Invalid email.")
        else:
            if not User.objects.filter(employee_id=login_input).exists():
                raise forms.ValidationError("Invalid employee ID.")

        return login_input


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current password'}),
        help_text="Enter a new password to change it or leave blank to keep the current password."
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Make password field optional for editing existing users
        if self.instance and self.instance.pk:
            self.fields['password'].required = False

    class Meta:
        model = User
        fields = [
            "email", "name", "phone_number", "mobile_number",
            "job_title", "email_enabled", "registration_date",
            "department", "role", "password", "is_admin", "is_article_writer", "is_approval_manager",
            "is_staff", "created_at", "status", "employee_id", "is_manager", "is_employee"
        ]

    def save(self, commit=True):
        user = super().save(commit=False)  # Get the user instance without saving
        password = self.cleaned_data.get("password")  # Get the cleaned password field

        if password:  # If a new password is provided
            print("Setting new password")
            user.set_password(password)
        else:  # If the password field is blank
            if user.pk:  # Check if the user exists in the database
                existing_user = User.objects.get(pk=user.pk)
                user.password = existing_user.password  # Retain the existing hashed password
            print("Keeping existing password")

        # Update status and role based on request data
        user.is_active = False
        if self.request and self.request.POST.get('status') != 'False':
            user.is_active = True

        role_fields = ["is_admin", "is_article_writer", "is_approval_manager", "is_staff","is_manager","is_employee"]

        # Ensure all roles are set to False first
        for role in role_fields:
            setattr(user, role, False)

        if self.request and hasattr(user, f'is_{self.request.POST.get("role", "")}'):
            setattr(user, f'is_{self.request.POST.get("role")}', True)

        # Save the user instance if commit=True
        if commit:
            user.save()

        return user


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """

    employee_id = forms.CharField(max_length=255, required=True, label=_("Employee ID"))

    class Meta:
        model = User
        fields = ["email", "employee_id", "password1", "password2"]

    def save(self, request):
        user = super().save(request)
        user.employee_id = self.cleaned_data['employee_id']
        user.save()
        return user


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """

class UserUploadForm(forms.Form):
    file = forms.FileField(
        required=True,
        help_text="Upload a CSV or Excel file.",
        widget=forms.FileInput(attrs={"accept": ".csv, .xlsx"}),
    )


class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop(
            "render_value", app_settings.PASSWORD_INPUT_RENDER_VALUE
        )
        kwargs["widget"] = forms.PasswordInput(
            render_value=render_value,
            attrs={"placeholder": kwargs.get("label")},
        )
        autocomplete = kwargs.pop("autocomplete", None)
        if autocomplete is not None:
            kwargs["widget"].attrs["autocomplete"] = autocomplete
        super(PasswordField, self).__init__(*args, **kwargs)




class SignupForm(BaseSignupForm):
    def __init__(self, *args, **kwargs):
        self.by_passkey = kwargs.pop("by_passkey", False)
        super().__init__(*args, **kwargs)
        password1_field = self._signup_fields.get("password1")
        if not self.by_passkey and password1_field:
            self.fields["password1"] = PasswordField(
                label=_("Password"),
                autocomplete="new-password",
                help_text=password_validation.password_validators_help_text_html(),
                required=password1_field["required"],
            )
            if "password2" in self._signup_fields:
                self.fields["password2"] = PasswordField(
                    label=_("Password (again)"),
                    autocomplete="new-password",
                    required=password1_field["required"],
                )

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

        honeypot_field_name = app_settings.SIGNUP_FORM_HONEYPOT_FIELD
        if honeypot_field_name:
            self.fields[honeypot_field_name] = forms.CharField(
                required=False,
                label="",
                widget=forms.TextInput(
                    attrs={
                        "style": "position: absolute; right: -99999px;",
                        "tabindex": "-1",
                        "autocomplete": "nope",
                    }
                ),
            )

    def try_save(self, request):
        """
        override of parent class method that adds additional catching
        of a potential bot filling out the honeypot field and returns a
        'fake' email verification response if honeypot was filled out
        """
        honeypot_field_name = app_settings.SIGNUP_FORM_HONEYPOT_FIELD
        if honeypot_field_name:
            if self.cleaned_data[honeypot_field_name]:
                user = None
                adapter = get_adapter()
                # honeypot fields work best when you do not report to the bot
                # that anything went wrong. So we return a fake email verification
                # sent response but without creating a user
                resp = adapter.respond_email_verification_sent(request, None)
                return user, resp

        return super().try_save(request)

    def clean(self):
        super().clean()

        # `password` cannot be of type `SetPasswordField`, as we don't
        # have a `User` yet. So, let's populate a dummy user to be used
        # for password validation.
        User = get_user_model()
        dummy_user = User()
        user_username(dummy_user, self.cleaned_data.get("username"))
        user_email(dummy_user, self.cleaned_data.get("email"))
        password = self.cleaned_data.get("password1")
        if password:
            try:
                get_adapter().clean_password(password, user=dummy_user)
            except forms.ValidationError as e:
                self.add_error("password1", e)

        if (
            "password2" in self._signup_fields
            and "password1" in self.cleaned_data
            and "password2" in self.cleaned_data
        ):
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                self.add_error(
                    "password2",
                    _("You must type the same password each time."),
                )
        return self.cleaned_data

    employee_id = forms.CharField(max_length=30, required=True, label="Employee ID")

    def save(self, request):
        # Call the parent save method to create the user object
        user = super(SignupForm, self).save(request)

        # Set the employee_id field on the user object
        user.employee_id = self.cleaned_data['employee_id']
        user.save()

        return user


