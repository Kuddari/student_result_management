# students/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='login_view'),
    path('home/', Home, name='home'),

    # path('student_report', Student_Rp, name='student_report'),
    path('sp_student_report', Student_Rp, name='sp_student_report'),
    path('gr_student_report', GR_Student, name='gr_student'),
    path('get-provinces', get_provinces, name='get-provinces'),
    path('get-districts', get_districts, name='get-districts'),
    path('get-subdistricts', get_subdistricts, name='get-subdistricts'),
    path('get-zipcode', get_zipcode, name='get_zipcode'),
    path('get-schools', get_schools, name='get-schools'),
    path('add-school', add_school, name='add-school'),
    path('profile/<int:student_id>/', Profile, name='profile'),

    # ดูเกรดนักเรียน
    path('student_results', student_Results, name='student_results'),

    # ใส่ข้อมูล
    path('ingr_student', student_marks_view, name='ingr_student'),

    # แก้ไขข้อมูล
    path('edit_profile', edit_Profile, name='edit_profile'),

    # เพิ่มข้อมูล
    path('in_profile', in_Profile, name='in_profile'),  # For creating a new profile
    path('in_profile/<int:student_id>', in_Profile, name='in_profile_edit'),  # For editing an existing profile
    

    # path('', student_list, name='student_list'),  # Student list page
    # path('register/', register_student, name='register'),  # Register student page
    # path('delete_student/<int:student_id>/', delete_student, name='delete_student'),
    # path('grading/', grading, name='grading'),
    path('download-pdf', download_students_pdf, name='download_students_pdf'),

]