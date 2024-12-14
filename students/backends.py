from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import Student, Teacher


class AuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        # Check if it's a student login
        try:
            # Authenticate student
            student = Student.objects.get(id=username, id_number=password)
            user, created = User.objects.get_or_create(username=student.id)
            if created:
                user.set_unusable_password()
                user.save()
            return user
        except Student.DoesNotExist:
            pass  # Continue to check for teacher

        try:
            # Authenticate teacher
            teacher = Teacher.objects.get(id=username, password=password)
            user, created = User.objects.get_or_create(username=teacher.id)
            if created:
                user.set_unusable_password()
                user.save()
            return user
        except Teacher.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None