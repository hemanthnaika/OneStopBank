from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()  # Dynamically fetch your custom user model

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find a user with the given email
            user = User.objects.get(email=username)
            if user.check_password(password):  # Check the password
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
