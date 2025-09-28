from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailOrEmployeeIDBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either email or employee_id.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # Check if username is an email or an employee_id
        try:
            # Check if the username contains '@' to determine if it's an email or employee_id
            if '@' in username:
                # Try to get a user by email with status 'True'
                user = UserModel.objects.get(status='True', email=username)
            else:
                # Try to get a user by employee_id with status 'True'
                user = UserModel.objects.get(status='True', employee_id=username)
        except UserModel.DoesNotExist:
            # Return None if no user is found
            return None

        if user.status != 'True':
            return None


        # Verify password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
