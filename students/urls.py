# students/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', Home, name='home'),
    path('sp_student_report', SP_Student, name='sp_student'),
    path('gr_student_report', GR_Student, name='gr_student')

    # path('', student_list, name='student_list'),  # Student list page
    # path('register/', register_student, name='register'),  # Register student page
    # path('delete_student/<int:student_id>/', delete_student, name='delete_student'),
    # path('grading/', grading, name='grading'),
]