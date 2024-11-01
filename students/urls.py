# students/urls.py

from django.urls import path
from .views import student_registration, student_list, student_profile

urlpatterns = [
    path('register/', student_registration, name='student_registration'),
    path('', student_list, name='student_list'),  # Home page with student list
    path('profile/<int:student_id>/', student_profile, name='student_profile'),  # Profile page
]
