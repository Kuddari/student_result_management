# students/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.db.models import Q
from django.contrib import messages
from decimal import Decimal
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer
from datetime import datetime  # Import the datetime module
pdfmetrics.registerFont(TTFont('THSarabunNew', 'static/fonts/THSarabunNew.ttf'))




def Home(request):
    # Get student data
    students = Student.objects.all()
    male_students = students.filter(gender='ชาย').count()
    female_students = students.filter(gender='หญิง').count()

    # Get special statuses
    orphans = students.filter(special_status='เด็กกำพร้า').count()
    underprivileged = students.filter(special_status='เด็กยากไร้').count()
    disabled = students.filter(special_status='เด็กพิการ').count()
    new_muslims = students.filter(special_status='เด็กมุอัลลัฟ').count()

    context = {
        'total_students': students.count(),
        'male_students': male_students,
        'female_students': female_students,
        'orphans': orphans,
        'underprivileged': underprivileged,
        'disabled': disabled,
        'new_muslims': new_muslims,
    }
    return render(request, 'home.html', context)



def Student_Rp(request):
    # รับค่าฟิลเตอร์
    search = request.GET.get('search', '').strip()
    school = request.GET.get('school')
    level = request.GET.get('level')
    academic_year = request.GET.get('academic_year')

    # Query นักเรียน
    students = Student.objects.filter(current_study__isnull=False)

    # กรองตามคำค้นหา
    if search:
        students = students.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )

    # กรองตามโรงเรียน
    if school:
        students = students.filter(current_study__school__id=school)

    # กรองตามระดับชั้น
    if level:
        students = students.filter(current_study__level__id=level)

    # กรองตามปีการศึกษา
    if academic_year:
        students = students.filter(current_study__current_semester__year=academic_year)

    # ดึงข้อมูลสำหรับตัวเลือก
    levels = Level.objects.all()
    schools = School.objects.all()
    academic_years = CurrentSemester.objects.values_list('year', flat=True).distinct()

    context = {
        'students': students,
        'total_students': students.count(),
        'male_students': students.filter(gender='ชาย').count(),
        'female_students': students.filter(gender='หญิง').count(),
        'levels': levels,
        'schools': schools,
        'academic_years': academic_years,
    }
    return render(request, 'student/sp_student.html', context)

def download_students_pdf(request):
    # รับค่าฟิลเตอร์จากคำร้องขอ (GET parameters)
    search = request.GET.get('search', '').strip()
    school = request.GET.get('school')
    level = request.GET.get('level')
    academic_year = request.GET.get('academic_year')

    # สร้าง Query นักเรียนตามฟิลเตอร์
    students_queryset = Student.objects.all()

    if search:
        students_queryset = students_queryset.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )
    if school:
        students_queryset = students_queryset.filter(current_study__school__id=school)
    if level:
        students_queryset = students_queryset.filter(current_study__level__id=level)
    if academic_year:
        students_queryset = students_queryset.filter(current_study__current_semester__year=academic_year)

    # เตรียมข้อมูลสำหรับ PDF
    students = [
        ['ลำดับ', 'ชื่อ', 'นามสกุล', 'เพศ', 'โรงเรียน', 'สถานะ'],  # หัวตาราง
    ]
    for i, student in enumerate(students_queryset, start=1):
        students.append([
            i,
            student.first_name,
            student.last_name,
            student.gender,
            student.current_study.school.name if student.current_study else 'ไม่มีข้อมูล',
            student.status,
        ])

    school_name = School.objects.get(id=school).name if school else "ทั้งหมด"
    level_name = Level.objects.get(id=level).name if level else "ทุกชั้น"
    academic_year_text = academic_year if academic_year else "ทุกปี"
    topic = f"<b>รายงานจำนวนนักเรียน</b>{school_name}  ชั้น: {level_name}  ปีการศึกษา: {academic_year_text}"

    # สร้าง Response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="students_report_{academic_year or "all"}.pdf"'
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(letter),
        topMargin=0.5 * inch,       # ระยะขอบบน 1 นิ้ว
        bottomMargin=0.5 * inch,    # ระยะขอบล่าง 1 นิ้ว
        leftMargin=0.5 * inch,    # ระยะขอบซ้าย 0.5 นิ้ว
        rightMargin=0.5 * inch    # ระยะขอบขวา 0.5 นิ้ว
    )

    # สร้างหัวข้อด้วย Paragraph
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'THSarabunNew'
    styles['Normal'].fontSize = 24
    styles['Normal'].alignment = 1  # 0=ซ้าย, 1=กลาง, 2=ขวา
    topic_paragraph = Paragraph(topic, styles['Normal'])

    # เพิ่มระยะห่างระหว่างหัวข้อกับตาราง
    spacer = Spacer(1, 0.5 * inch)
    # สร้าง PDF
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    # สร้างตาราง
    table = Table(students, colWidths=[50, 150, 150, 100, 200, 100])

    # ปรับแต่งตาราง
    style = TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'THSarabunNew'),
        ('FONTSIZE', (0, 0), (-1, 0), 16),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),

        ('FONTNAME', (0, 1), (-1, -1), 'THSarabunNew'),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    table.setStyle(style)

    # เพิ่มหัวข้อและตารางลงใน PDF
    elements = [topic_paragraph, spacer, table]
    doc.build(elements)

    return response


def GR_Student (request):
    return render(request, 'student/gr_student.html')

# def student_list(request):
#     # Fetch all filter options
#     schools = School.objects.all()
#     levels = Level.objects.all()
#     semesters = Semester.objects.all()

#     # Start with all students
#     students = Student.objects.select_related('current_study', 'current_study__level', 'current_study__semester')

#     # Apply filters based on GET parameters
#     school_id = request.GET.get('school')
#     year_level_id = request.GET.get('year_level')
#     semester_id = request.GET.get('semester')

#     if school_id:
#         students = students.filter(current_study__school__id=school_id)
#     if year_level_id:
#         students = students.filter(current_study__level__id=year_level_id)
#     if semester_id:
#         students = students.filter(current_study__semester__id=semester_id)

#     context = {
#         'students': students,
#         'schools': schools,
#         'levels': levels,
#         'semesters': semesters,
#     }
#     return render(request, 'students/student_list.html', context)


# def register_student(request):
#     if request.method == 'POST':
#         # Address Information
#         address = Address(
#             house_number=request.POST['house_number'],
#             street=request.POST['street'],
#             subdistrict=request.POST['subdistrict'],
#             district=request.POST['district'],
#             province=request.POST['province'],
#             postal_code=request.POST['postal_code'],
#             contact_number=request.POST['contact_number']
#         )
#         address.save()  # Save the address first

#         # Student Information
#         student = Student(
#             first_name=request.POST['first_name'],
#             last_name=request.POST['last_name'],
#             english_name=request.POST.get('english_name', ''),
#             arabic_name=request.POST.get('arabic_name', ''),
#             date_of_birth=request.POST['date_of_birth'],
#             id_number=request.POST['id_number'],
#             address=address,  # Link the address
#             special_status=request.POST.get('special_status'),
#             profile_picture=request.FILES.get('profile_picture', None)  # Handle file upload
            
#         )
#         student.save()  # Save the student

#         # Parents Information
#         father = Father(
#             student=student,
#             first_name=request.POST['father_first_name'],
#             last_name=request.POST['father_last_name'],
#             date_of_birth=request.POST['father_date_of_birth'],
#             address=address,  # Link the address
#             occupation=request.POST.get('father_occupation', None),  # Assuming these fields exist
#             workplace=request.POST.get('father_workplace', None),
#             income=request.POST.get('father_income', None),
#             phone_number=request.POST.get('father_phone_number', None)
#         )
#         father.save()

#         mother = Mother(
#             student=student,
#             first_name=request.POST['mother_first_name'],
#             last_name=request.POST['mother_last_name'],
#             date_of_birth=request.POST['mother_date_of_birth'],
#             address=address,  # Link the address
#             occupation=request.POST.get('mother_occupation', None),
#             workplace=request.POST.get('mother_workplace', None),
#             income=request.POST.get('mother_income', None),
#             phone_number=request.POST.get('mother_phone_number', None)
#         )
#         mother.save()

#         # Guardian Information (if applicable)
#         guardian_first_name = request.POST.get('guardian_first_name', '')
#         if guardian_first_name:  # Only create if there's a guardian
#             guardian = Guardian(
#                 student=student,
#                 first_name=guardian_first_name,
#                 last_name=request.POST.get('guardian_last_name', ''),
#                 date_of_birth=request.POST.get('guardian_date_of_birth', None),
#                 address=address,  # Link the address
#                 relationship_with_student=request.POST.get('relationship_with_student', ''),
#                 occupation=request.POST.get('guardian_occupation', None),
#                 workplace=request.POST.get('guardian_workplace', None),
#                 income=request.POST.get('guardian_income', None),
#                 phone_number=request.POST.get('guardian_phone_number', None)
#             )
#             guardian.save()

#         messages.success(request, 'ลงทะเบียนนักเรียนเรียบร้อยแล้ว')
#         return redirect('student_list')  
#     return render(request, 'students/student_registration.html')

# def delete_student(request, student_id):
#     student = get_object_or_404(Student, id=student_id)  # Get the student or 404 if not found
#     if request.method == 'POST':
#         student.delete()  # Delete the student record
#         return redirect('student_list')  # Redirect to the student list page after deletion
#     return render(request, 'delete_student.html', {'student': student})

# def grading(request): 
#     # Fetch all necessary data
#     students = Student.objects.all()
#     subjects_to_study = SubjectToStudy.objects.all()
#     levels = Level.objects.all()
#     semesters = Semester.objects.all()
#     schools = School.objects.all()
    
#     # Get filter parameters from the request
#     selected_school = request.GET.get('school_id')
#     selected_level = request.GET.get('level_id')
#     selected_semester = request.GET.get('semester_id')

#     # Apply filters for school, level, and semester
#     if selected_school:
#         students = students.filter(current_study__school__id=selected_school)
#     if selected_level:
#         students = students.filter(current_study__level__id=selected_level)
#     if selected_semester:
#         students = students.filter(current_study__semester__id=selected_semester)
#         subjects_to_study = subjects_to_study.filter(semester__id=selected_semester)

#     # Prepare a dictionary to hold obtained marks for each student and subject
#     obtained_marks = {}
#     total_marks = {}
#     total_obtained_marks = {}
    
#     for student in students:
#         obtained_marks[student.id] = {}
#         total_marks[student.id] = 0
#         total_obtained_marks[student.id] = 0
        
#         for subject in subjects_to_study:
#             mark_entry = StudentMarkForSubject.objects.filter(
#                 student=student,
#                 subject_to_study=subject
#             ).first()
#             marks_obtained = mark_entry.marks_obtained if mark_entry else 0
#             obtained_marks[student.id][subject.id] = marks_obtained
            
#             # Calculate total marks and obtained marks
#             total_marks[student.id] += subject.subject.total_marks
#             total_obtained_marks[student.id] += marks_obtained

#     # Handle form submission
#     if request.method == "POST":
#         for student_id in request.POST.getlist('student_id'):
#             student = Student.objects.get(id=student_id)
#             for subject in subjects_to_study:
#                 marks_obtained = request.POST.get(f'marks_{student_id}_{subject.id}')
#                 if marks_obtained:
#                     StudentMarkForSubject.objects.update_or_create(
#                         student=student,
#                         subject_to_study=subject,
#                         defaults={'marks_obtained': marks_obtained}
#                     )
#         return redirect('grading')  # Redirect to the grading view after submission

#     # Context for the template
#     context = {
#         'students': students,
#         'subjects_to_study': subjects_to_study,
#         'levels': levels,
#         'semesters': semesters,
#         'schools': schools,
#         'obtained_marks': obtained_marks,
#         'total_marks': total_marks,
#         'total_obtained_marks': total_obtained_marks,
#         'selected_school': selected_school,
#         'selected_level': selected_level,
#         'selected_semester': selected_semester,
#     }
#     return render(request, 'students/grading.html', context)


# def gradings(request): 
#     # Fetch all necessary data
#     students = Student.objects.all()
#     subjects_to_study = SubjectToStudy.objects.all()
#     levels = Level.objects.all()
#     semesters = Semester.objects.all()
#     schools = School.objects.all()
    
#     # Get filter parameters from the request
#     selected_school = request.GET.get('school_id')
#     selected_level = request.GET.get('level_id')
#     selected_semester = request.GET.get('semester_id')

#     # Apply filters for school, level, and semester
#     if selected_school:
#         students = students.filter(current_study__school__id=selected_school)
#     if selected_level:
#         students = students.filter(current_study__level__id=selected_level)
#     if selected_semester:
#         students = students.filter(current_study__semester__id=selected_semester)
#         subjects_to_study = subjects_to_study.filter(semester__id=selected_semester)

#      # Prepare a dictionary to hold obtained marks for each student and subject
#     obtained_marks = {}
#     total_marks = {}
#     total_obtained_marks = {}
    
#     for student in students:
#         obtained_marks[student.id] = {}
#         total_marks[student.id] = 0
#         total_obtained_marks[student.id] = 0
        
#         for subject in subjects_to_study:
#             mark_entry = StudentMarkForSubject.objects.filter(
#                 student=student,
#                 subject_to_study=subject
#             ).first()
            
#             obtained_mark = mark_entry.marks_obtained if mark_entry else 0
#             obtained_marks[student.id][subject.id] = obtained_mark
            
#             # Accumulate total marks and obtained marks
#             total_marks[student.id] += subject.subject.total_marks  # Assuming `subject.subject.total_marks` gives full marks for the subject
#             total_obtained_marks[student.id] += obtained_mark  # Add obtained marks for this subject

#     # Handle form submission
#     if request.method == "POST":
#         for student_id in request.POST.getlist('student_id'):
#             student = Student.objects.get(id=student_id)
#             for subject in subjects_to_study:
#                 marks_obtained = request.POST.get(f'marks_{student_id}_{subject.id}')
#                 if marks_obtained:
#                     StudentMarkForSubject.objects.update_or_create(
#                         student=student,
#                         subject_to_study=subject,
#                         defaults={'marks_obtained': marks_obtained}
#                     )
#         return redirect('grading')  # Redirect to the grading view after submission

#     # Context for the template
#     context = {
#         'students': students,
#         'subjects_to_study': subjects_to_study,
#         'levels': levels,
#         'semesters': semesters,
#         'schools': schools,
#         'obtained_marks': obtained_marks,  # Add obtained marks to context
#         'total_marks' : total_marks,
#         'total_obtained_marks': total_obtained_marks,
#         'selected_school': selected_school,
#         'selected_level': selected_level,
#         'selected_semester': selected_semester,
#     }
#     return render(request, 'students/grading.html', context)
