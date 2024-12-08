# students/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', Home, name='home'),
    # path('student_report', Student_Rp, name='student_report'),
    path('sp_student_report', Student_Rp, name='sp_student_report'),
    path('gr_student_report', GR_Student, name='gr_student'),
    path('admin/get-districts/', get_districts, name='get-districts'),
    path('admin/get-subdistricts/', get_subdistricts, name='get-subdistricts'),
    path('admin/get-postal-code/', get_postal_code, name='get-postal-code'),

    # ใส่ข้อมูล
    path('ingr_student', student_marks_view, name='ingr_student'),


    # path('', student_list, name='student_list'),  # Student list page
    # path('register/', register_student, name='register'),  # Register student page
    # path('delete_student/<int:student_id>/', delete_student, name='delete_student'),
    # path('grading/', grading, name='grading'),
    path('download-pdf/', download_students_pdf, name='download_students_pdf'),

]