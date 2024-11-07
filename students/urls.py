# students/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', student_list, name='student_list'),  # Student list page
    path('register/', register_student, name='register'),  # Register student page
    path('delete_student/<int:student_id>/', delete_student, name='delete_student'),
    path('grading/', grading, name='grading'),
]