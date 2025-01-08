# students/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.db.models import Q, F, FloatField, ExpressionWrapper
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime  # Import the datetime module
from django.views.decorators.csrf import csrf_exempt
import json
from urllib.parse import urlencode
from django.core.paginator import Paginator


pdfmetrics.registerFont(TTFont('THSarabunNew', 'static/fonts/THSarabunNew.ttf'))

def convert_to_thai_year(academic_year):
    # Assuming academic year is in the format "2023-2024", convert to Thai year
    year_parts = academic_year.split('-')
    thai_year = int(year_parts[0]) + 543  # Thai year is 543 years ahead of Gregorian year
    return f"{thai_year}-{int(year_parts[1]) + 543}"

def delete_student(request, student_id):
    # Fetch the student by ID

    # Check if 'user_type' is in the session
    user_type = request.session.get('user_type')
    
    # If no user_type is found, redirect to login
    if not user_type:
        return redirect('login_view')  # Redirect to login if user_type is not in session

    # If user is not a teacher, redirect to home
    if user_type == 'student':
        return redirect('home')  # Redirect student back to home
    
    student = get_object_or_404(Student, id=student_id)
    # Soft delete the student by setting delete_status to 'deleted'
    student.delete_status = 'deleted'
    student.save()

    # Redirect back to the student report page
    return redirect('sp_student_report')  # Replace 'student_report' with the correct URL name for your student list page

def get_schools(request):
    schools = list(School.objects.values('id', 'name'))
    return JsonResponse(schools, safe=False)

def safe_int(value):
    """Convert a value to int or return 0 if it's not valid."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

def add_school(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        school_name = data.get('name')
        if school_name:
            school, created = School.objects.get_or_create(name=school_name)
            return JsonResponse({'id': school.id, 'name': school.name})
        return JsonResponse({'error': 'Invalid data'}, status=400)
                            
def get_provinces(request):
    provinces = list(Province.objects.all().values('id', 'name'))
    return JsonResponse(provinces, safe=False)



# Get districts (amphoes) based on the selected province
def get_districts(request):
    province_id = request.GET.get('province_id')
    if not province_id:
        return JsonResponse({'error': 'Invalid province ID'}, status=400)
    
    districts = list(Amphoe.objects.filter(province_id=province_id).values('id', 'name'))
    return JsonResponse(districts, safe=False)

# Get subdistricts (tambons) based on the selected district
def get_subdistricts(request):
    district_id = request.GET.get('district_id')
    if not district_id:
        return JsonResponse({'error': 'Invalid district ID'}, status=400)
    
    subdistricts = list(Tambon.objects.filter(amphoe_id=district_id).values('id', 'name'))
    return JsonResponse(subdistricts, safe=False)

# Fetch zipcode based on subdistrict
def get_zipcode(request):
    subdistrict_id = request.GET.get('subdistrict_id')
    subdistrict = Tambon.objects.filter(id=subdistrict_id).first()
    if subdistrict:
        return JsonResponse({'zipcode': subdistrict.zipcode})
    return JsonResponse({'zipcode': ''})

#Auth 
def login_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')  # User ID input
        password = request.POST.get('password')  # User's password
        remember_me = request.POST.get('remember_me')  # Checkbox value

        # Validate input
        if not user_id or not password:
            return render(request, 'auth/login.html', {
                'error_message': 'กรุณาใส่ไอดีผู้ใช้และรหัสผ่าน',  # "Please enter both user ID and password"
            })

        # Authenticate the user
        user = authenticate(request, username=user_id, password=password)

        if user is not None:
            # Log the user in
            login(request, user)

            # Set session expiration based on "Remember Me"
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Browser close to expire the session

            # Set session data based on user type
            if user.is_superuser:  # Check if the user is a superuser
                request.session['user_type'] = 'superuser'
                return redirect('home')  # Redirect superusers to the admin dashboard
            elif Student.objects.filter(id=user_id, delete_status='not_deleted').exists():
                request.session['user_type'] = 'student'
                request.session['student_id'] = user_id
                return redirect('home')  # Redirect students to the home page
            elif Teacher.objects.filter(id=user_id).exists():
                request.session['user_type'] = 'teacher'
                request.session['teacher_id'] = user_id
                return redirect('home')  # Redirect teachers to the home page
            else:
                # Log the user out if the category is unknown
                logout(request)
                return render(request, 'auth/login.html', {
                    'error_message': 'ไม่สามารถเข้าสู่ระบบได้',  # "Unable to log in"
                })
        else:
            # Authentication failed
            return render(request, 'auth/login.html', {
                'error_message': 'ไอดีผู้ใช้หรือรหัสผ่านไม่ถูกต้อง',  # "Incorrect user ID or password"
            })

    # For GET requests, render the login page
    return render(request, 'auth/login.html')

# Auth
def logout_view(request):
    # Log the user out
    logout(request)
    
    # Redirect to login page after logout
    return redirect('login_view')  # Replace 'login' with the name of your login URL

#Home page
def Home(request):

    # Check if 'user_type' is in the session
    user_type = request.session.get('user_type')
    
    if not user_type:
        return redirect('login_view')  # Redirect to login if no user_type is found in session


    if user_type == 'student' and 'student_id' in request.session:
        user_id = request.session['student_id']
        
        # Get student data
        try:
            student = Student.objects.get(id=user_id)
        except Student.DoesNotExist:
            return redirect('login_view')  # Redirect if student not found

        # Get student statistics
        students = Student.objects.filter(delete_status='not_deleted')
        male_students = students.filter(gender='ชาย').count()
        female_students = students.filter(gender='หญิง').count()
        orphans = students.filter(special_status='เด็กกำพร้า').count()
        underprivileged = students.filter(special_status='เด็กยากไร้').count()
        disabled = students.filter(special_status='เด็กพิการ').count()
        new_muslims = students.filter(special_status='เด็กมุอัลลัฟ').count()

        context = {
            'user_type': user_type,
            'total_students': students.count(),
            'male_students': male_students,
            'female_students': female_students,
            'orphans': orphans,
            'underprivileged': underprivileged,
            'disabled': disabled,
            'new_muslims': new_muslims,
            'student': student
        }
        return render(request, 'student_home.html', context)
    
    elif user_type in ['teacher', 'superuser']:
        
        # Get student statistics
        students = Student.objects.filter(delete_status='not_deleted')
        male_students = students.filter(gender='ชาย').count()
        female_students = students.filter(gender='หญิง').count()
        orphans = students.filter(special_status='เด็กกำพร้า').count()
        underprivileged = students.filter(special_status='เด็กยากไร้').count()
        disabled = students.filter(special_status='เด็กพิการ').count()
        new_muslims = students.filter(special_status='เด็กมุอัลลัฟ').count()

        context = {
            'user_type': user_type,
            'total_students': students.count(),
            'male_students': male_students,
            'female_students': female_students,
            'orphans': orphans,
            'underprivileged': underprivileged,
            'disabled': disabled,
            'new_muslims': new_muslims,
        }
        return render(request, 'teacher_home.html', context)
    else:
        return redirect('login_view')  # Redirect for unauthorized access
    
#students input
def Input_Profile(request, student_id=None):
    # Check if 'user_type' is in the session
    user_type = request.session.get('user_type')
    
    # If no user_type is found, redirect to login
    if not user_type:
        return redirect('login_view')  # Redirect to login if user_type is not in session
    
    provinces = Province.objects.all()
    schools = School.objects.all()
    levels = Level.objects.all()

    student = None
    father, mother, guardian, current_study = None, None, None, None

    if student_id:
        student = get_object_or_404(Student, id=student_id)
        father = Father.objects.filter(student=student).first()
        mother = Mother.objects.filter(student=student).first()
        guardian = Guardian.objects.filter(student=student).first()
        current_study = CurrentStudy.objects.filter(student=student).first()

    if request.method == 'POST':
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                return None

        def safe_int(value):
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        def handle_address(prefix):
            address_data = {
                'house_number': request.POST.get(f'{prefix}-house-number'),
                'street': request.POST.get(f'{prefix}-street'),
                'moo': safe_int(request.POST.get(f'{prefix}-village')),
                'province_id': request.POST.get(f'{prefix}-province'),
                'district_id': request.POST.get(f'{prefix}-district'),
                'subdistrict_id': request.POST.get(f'{prefix}-subdistrict'),
                'zipcode': request.POST.get(f'{prefix}-zipcode'),
            }
            return Address.objects.create(**address_data)

        # Student Data
        student_data = {
            'first_name': request.POST.get('student-first-name'),
            'last_name': request.POST.get('student-last-name'),
            'english_first_name': request.POST.get('student-english-first-name'),
            'english_last_name': request.POST.get('student-english-last-name'),
            'arabic_first_name': request.POST.get('student-arabic-first-name'),
            'arabic_last_name': request.POST.get('student-arabic-last-name'),
            'date_of_birth': parse_date(request.POST.get('student-dob')),
            'id_number': request.POST.get('student-id-number', '').replace(' ', ''),
            'special_status': request.POST.get('special-status'),
            'gender': request.POST.get('gender'),
        }

        # Validate ID number
        if not student_data['id_number'].isdigit() or len(student_data['id_number']) != 13:
            return JsonResponse({'error': 'Invalid Thai ID number. It must contain exactly 13 digits.'}, status=400)

        if student:
            for field, value in student_data.items():
                setattr(student, field, value)
            if 'profile_picture' in request.FILES:
                student.profile_picture = request.FILES['profile_picture']
            student.save()
        else:
            student = Student.objects.create(
                **student_data,
                profile_picture=request.FILES.get('profile_picture', None)
            )

        # Current Study
        school_id = request.POST.get('student-school')
        level_id = request.POST.get('student-level')
        student_school = get_object_or_404(School, id=school_id) if school_id else None
        level = Level.objects.get(id=level_id) if level_id else None

        if current_study:
            current_study.school = student_school
            current_study.level = level
            current_study.save()
        else:
            if student_school:
                CurrentStudy.objects.create(student=student, school=student_school, level=level)

        # Family Data
        for role, model in [('father', Father), ('mother', Mother), ('guardian', Guardian)]:
            address = handle_address(role)
            data = {
                'first_name': request.POST.get(f'{role}-first-name'),
                'last_name': request.POST.get(f'{role}-last-name'),
                'date_of_birth': parse_date(request.POST.get(f'{role}-dob')),
                'phone_number': request.POST.get(f'{role}-phone'),
                'occupation': request.POST.get(f'{role}-occupation'),
                'workplace': request.POST.get(f'{role}-workplace'),
                'income': safe_int(request.POST.get(f'{role}-income')),
                'address': address,
            }
            if role == 'guardian':
                data['relationship_with_student'] = request.POST.get('relationship')
            model.objects.update_or_create(student=student, defaults=data)

        return redirect('profile', student_id=student.id)

    return render(request, 'inputdata/in_profile.html', {
        'levels': levels,
        'provinces': provinces,
        'schools': schools,
        'student': student,
        'father': father,
        'mother': mother,
        'guardian': guardian,
        'current_study': current_study
    })

def Profile(request, student_id=None):
    # Check if 'user_type' is in the session
    user_type = request.session.get('user_type')
    
    # If no user_type is found, redirect to login
    if not user_type:
        return redirect('login_view')  # Redirect to login if user_type is not in session
    
    if not student_id:
        return redirect('login_view')  # Redirect to login if student_id is not provided

    # Get the student instance or return 404 if not found
    student = get_object_or_404(Student, id=student_id)
    
    # Fetch related data
    current_study = CurrentStudy.objects.filter(student=student).first()
    father = Father.objects.filter(student=student).first()
    mother = Mother.objects.filter(student=student).first()
    guardian = Guardian.objects.filter(student=student).first()

    # Pass the data to the template
    context = {
        'student': student,
        'current_study': current_study,
        'father': father,
        'mother': mother,
        'guardian': guardian,
    }

    return render(request, 'student/profile.html', context)

from django.core.paginator import Paginator

def Student_Rp(request):
    # Check if 'user_type' is in the session
    user_type = request.session.get('user_type')
    if not user_type:
        return redirect('login_view')
    if user_type == 'student':
        return redirect('home')

    # รับค่าฟิลเตอร์
    search = request.GET.get('search', '').strip()
    school = request.GET.get('school')
    level = request.GET.get('level')
    academic_year = request.GET.get('academic_year')
    gender = request.GET.get('gender')
    special_status = request.GET.get('special_status')
    action = request.GET.get('action')
    items_per_page = int(request.GET.get('items_per_page', 10))  # รับค่าจำนวนข้อมูลต่อหน้า (ค่าเริ่มต้นคือ 10)

    # Query นักเรียน
    students = Student.objects.filter(current_study__isnull=False, delete_status='not_deleted')

    if search:
        students = students.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )
    if school:
        students = students.filter(current_study__school__id=school)
    if level:
        students = students.filter(current_study__level__id=level)
    if academic_year:
        students = students.filter(current_study__current_semester__year=academic_year)
    if gender:
        students = students.filter(gender=gender)
    if special_status:
        students = students.filter(special_status=special_status)

    if action == 'download':
        return download_students_pdf(students)

    # Pagination
    paginator = Paginator(students, items_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # ดึงข้อมูลสำหรับตัวเลือก
    levels = Level.objects.all()
    schools = School.objects.all()
    academic_years = CurrentSemester.objects.values_list('year', flat=True).distinct()

    # สร้าง URL ที่รวมฟิลเตอร์ทั้งหมด
    query_params = request.GET.copy()
    query_params.pop('page', None)  # ลบพารามิเตอร์ page ออกเพื่อไม่ให้ URL ซ้ำกัน
    filter_params = query_params.urlencode()  # สร้าง URL ของพารามิเตอร์ที่เหลือ

    context = {
        'page_obj': page_obj,
        'total_students': students.count(),
        'male_students': students.filter(gender='ชาย').count(),
        'female_students': students.filter(gender='หญิง').count(),
        'levels': levels,
        'schools': schools,
        'academic_years': academic_years,
        'current_filters': {
            'search': search,
            'school': school,
            'level': level,
            'academic_year': academic_year,
            'gender': gender,
            'special_status': special_status,
            'items_per_page': items_per_page,
        },
        'filter_params': filter_params,  # ส่งค่าพารามิเตอร์ฟิลเตอร์
    }

    return render(request, 'student/sp_student.html', context)


def download_students_pdf(students):
    # Check if there are any students
    if not students.exists():
        student_data = [['ไม่มีข้อมูล']]
    else:
        student_data = [
            ['ลำดับ', 'ชื่อ', 'นามสกุล', 'เพศ', 'โรงเรียน', 'สถานะพิเศษ'],
        ]
        for i, student in enumerate(students, start=1):
            student_data.append([
                i,
                student.first_name,
                student.last_name,
                student.gender or 'ไม่มีข้อมูล',
                student.current_study.school.name if student.current_study else 'ไม่มีข้อมูล',
                student.special_status or 'ไม่มีข้อมูล',
            ])


    
    # Dynamically determine unique values from the queryset
    unique_genders = students.values_list('gender', flat=True).distinct()
    unique_special_statuses = students.values_list('special_status', flat=True).distinct()
    unique_schools = students.values_list('current_study__school__name', flat=True).distinct()
    unique_levels = students.values_list('current_study__level__name', flat=True).distinct()
    unique_academic_years = students.values_list('current_study__current_semester__year', flat=True).distinct()

    # Function to handle the display logic based on the number of unique values
    def get_unique_text(unique_values, default_text):
        if len(unique_values) == 1:
            return unique_values[0]
        return default_text

    # Gender and Special Status Text
    gender_text = get_unique_text(unique_genders, "ทุกเพศ")
    status_text = get_unique_text(unique_special_statuses, "ทุกสถานะพิเศษ")
    # School, Level, and Academic Year Text
    school_name = get_unique_text(unique_schools, "ทุกโรงเรียน")
    level_name = get_unique_text(unique_levels, "ทุกชั้น")
    academic_year_text = get_unique_text(unique_academic_years, "ทุกปี")

    header_info = f"ชั้น: {level_name} | ปีการศึกษา: {academic_year_text} | เพศ: {gender_text} | สถานะพิเศษ: {status_text}"
    

    # Create PDF Response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="students_report_{academic_year_text or "all"}.pdf"'

    # Create PDF Document (A4 Landscape)
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    # Logo
    logo_path = "static/images/logo.png"
    logo = Image(logo_path, width=1 * inch, height=1 * inch)

    # School Title
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'THSarabunNew'
    styles['Normal'].fontSize = 20
    styles['Normal'].alignment = 1
    school_paragraph = Paragraph(f"<b>{school_name}</b>", styles['Normal'])

    # Info Paragraph
    # Custom Style for Info Paragraph
    custom_style = styles['Normal'].clone('CustomNormal')
    custom_style.fontName = 'THSarabunNew'
    custom_style.fontSize = 18
    custom_style.leading = 16  # เพิ่มระยะห่างระหว่างบรรทัด
    custom_style.alignment = 1

    # Info Paragraph
    info_paragraph = Paragraph(header_info, custom_style)

    # Header Table Layout
    header_table_data = [
        [logo, school_paragraph, info_paragraph]
    ]
    header_table = Table(
        header_table_data,
        colWidths=[2 * inch, 5 * inch, 3 * inch]
    )
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (1, 0), (-1, -1), 15),
    ]))

    # Add spacing
    spacer = Spacer(1, 0.3 * inch)

    # Student Table
    table = Table(
        student_data,
        colWidths=[50, 150, 150, 100, 250, 100]
    )
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'THSarabunNew'),
        ('FONTSIZE', (0, 0), (-1, 0), 16),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),

        ('FONTNAME', (0, 1), (-1, -1), 'THSarabunNew'),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    # Build PDF
    elements = [header_table, spacer, table]
    doc.build(elements)

    return response

#grade input
def student_marks_view(request):
     # Check if 'user_type' is in the session
    user_type = request.session.get('user_type')
    
    # If no user_type is found, redirect to login
    if not user_type:
        return redirect('login_view')  # Redirect to login if user_type is not in session

    # If user is not a teacher, redirect to home
    if user_type == 'student':
        return redirect('home')  # Redirect student back to home

    current_semester = CurrentSemester.objects.first()

    if not current_semester:
        return render(request, 'inputdata/ingr_student.html', {'error': 'Current semester not set.'})

    # Filters from GET request
    school_name = request.GET.get('school')
    level_name = request.GET.get('level')

    # Fetch filter options
    schools = School.objects.all()
    levels = Level.objects.all()

    students = []
    subjects = []
    student_marks_data = []  # Holds marks for rendering in the template

    if school_name and level_name:
        # Query students and subjects based on filters
        students_query = CurrentStudy.objects.filter(
            current_semester=current_semester,
            school__name__iexact=school_name,
            level__name__iexact=level_name,
        ).select_related('student', 'level', 'school')

        students = list(students_query)

        subjects = SubjectToStudy.objects.filter(
            level__name__iexact=level_name,
            semester=current_semester.semester,
        ).select_related('subject')

        # Fetch marks for students and prepare data structure
        for student in students:
            marks_row = {'student': student.student}
            for subject in subjects:
                mark_obj = StudentMarkForSubject.objects.filter(
                    student=student.student,
                    subject_to_study=subject
                ).first()
                marks_row[subject.subject.id] = mark_obj.marks_obtained if mark_obj else ''
            student_marks_data.append(marks_row)

    if request.method == 'POST':
        # Handle form submission
        students_query = CurrentStudy.objects.filter(
            current_semester=current_semester,
            school__name__iexact=school_name,
            level__name__iexact=level_name,
            student__delete_status='not_deleted'
        ).select_related('student', 'level', 'school')

        subjects = SubjectToStudy.objects.filter(
            level__name__iexact=level_name,
            semester=current_semester.semester,
        ).select_related('subject')

        for student in students_query:
            student_subject_marks = {}
            total_marks = 0
            obtained_marks = 0

            for subject in subjects:
                field_name = f"marks_{student.student.id}_{subject.subject.id}"
                marks = request.POST.get(field_name)

                if marks:
                    try:
                        marks = int(marks)
                        student_subject_marks[subject.subject.name] = marks
                        total_marks += subject.subject.total_marks
                        obtained_marks += marks

                        # Save to StudentMarkForSubject
                        StudentMarkForSubject.objects.update_or_create(
                            student=student.student,
                            subject_to_study=subject,
                            defaults={'marks_obtained': marks},
                        )
                    except ValueError:
                        return render(request, 'inputdata/ingr_student.html', {
                            'error': f"Invalid marks for {student.student.first_name} in {subject.subject.name}.",
                            'schools': schools,
                            'levels': levels,
                            'students': students,
                            'subjects': subjects,
                        })

            # Save to StudentHistory
            if total_marks > 0:
                grade_percentage = (obtained_marks / total_marks) * 100
            else:
                grade_percentage = 0

            StudentHistory.objects.update_or_create(
                student_id=student.student.id,
                student_name=f"{student.student.first_name} {student.student.last_name}",
                school_name=student.school.name,
                level_name=student.level.name,
                semester=current_semester.semester,
                academic_year=current_semester.year,
                defaults={
                    'total_marks': total_marks,
                    'obtained_marks': obtained_marks,
                    'grade_percentage': grade_percentage,
                    'subject_marks': student_subject_marks,
                    'pass_or_fail': "ผ่าน" if grade_percentage >= 50 else "ไม่ผ่าน"
                }
            )
        academic_year = current_semester.year
        # Filter out None values
        # Build query parameters for redirection
        query_params = {
            'school': school_name,
            'level': level_name,
            'academic_year': academic_year
        }
        # Remove None values
        query_params = {key: value for key, value in query_params.items() if value}

        # Reverse the URL and append query parameters
        base_url = reverse('gr_student')  # Ensure this matches urls.py name
        redirect_url = f"{base_url}?{urlencode(query_params)}"

        return HttpResponseRedirect(redirect_url)
        # Build the redirection URL with query string
       
    context = {
        'user_type': user_type,
        'schools': schools,
        'levels': levels,
        'students': students,
        'subjects': subjects,
        'current_semester': current_semester,
        'student_marks_data': student_marks_data,
    }

    return render(request, 'inputdata/ingr_student.html', context)


#grade output
def GR_Student(request):
    # Check if 'user_type' is in the session
    user_type = request.session.get('user_type')
    
    # If no user_type is found, redirect to login
    if not user_type:
        return redirect('login_view')  # Redirect to login if user_type is not in session

    # If user is not a teacher, redirect to home
    if user_type == 'student':
        return redirect('home')  # Redirect student back to home

    # Continue with the view if user_type is 'teacher'
    # Fetch filter options
    schools = School.objects.all()
    levels = Level.objects.all()
    current_semester = CurrentSemester.objects.first()

    # Fetch unique academic years from StudentHistory
    academic_years = StudentHistory.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year')

    # Get filters from the GET request
    school_name = request.GET.get('school')
    level_name = request.GET.get('level')
    academic_year = request.GET.get('academic_year', current_semester.year if current_semester else None)

    # Filtered query
    histories = StudentHistory.objects.all()

    if school_name:
        histories = histories.filter(school_name=school_name)

    if level_name:
        histories = histories.filter(level_name=level_name)

    if academic_year:
        histories = histories.filter(academic_year=academic_year)

    # Extract subjects dynamically (assuming subject marks are stored in JSON format)
    subjects = []
    if histories.exists():
        first_entry = histories.first()
        subjects = first_entry.subject_marks.keys() if first_entry.subject_marks else []
    
    # Fetch total marks for each subject (assuming SubjectToStudy holds subject and total marks)
    subject_totals = {}
    if level_name and current_semester:
        subject_to_studies = SubjectToStudy.objects.filter(
            level__name__iexact=level_name,
            semester=current_semester.semester
        ).select_related('subject')

        subject_totals = {subject.subject.name: subject.subject.total_marks for subject in subject_to_studies}

    context = {
        'user_type': user_type,
        'schools': schools,
        'levels': levels,
        'academic_years': academic_years,
        'students': histories,
        'subjects': subjects,
        'subject_totals': subject_totals,
        'academic_year': academic_year,
        'current_semester': current_semester,
        'school_name': school_name,
        'level_name': level_name,
        'academic_year': academic_year,
    }

    return render(request, 'student/gr_student.html', context)

def student_Results(request, student_id):
    user_type = request.session.get('user_type')

    if not user_type:
        return redirect('login_view')

    student = get_object_or_404(Student, id=student_id)
    current_study = CurrentStudy.objects.filter(student=student).first()
    current_semester = CurrentSemester.objects.first()

    academic_years = StudentHistory.objects.filter(student_id=student.id).values_list('academic_year', flat=True).distinct().order_by('-academic_year')
    selected_academic_year = request.GET.get('academic_year') or (academic_years.first() if academic_years else (current_semester.year if current_semester else None))

    student_history_instance = StudentHistory.objects.filter(
    student_id=student.id, academic_year=selected_academic_year
    ).first()

    subjects_cat1_data = student_history_instance.get_subject_data(category=1) if student_history_instance else []
    subjects_cat2_data = student_history_instance.get_subject_data(category=2) if student_history_instance else []

    if 'download_pdf' in request.GET:
        category_1_data = [
            (s['name'], s['marks'], s['percentage'], s['status']) for s in subjects_cat1_data
        ]
        category_2_data = [
            (s['name'], s['marks'], s['percentage'], s['status']) for s in subjects_cat2_data
        ]

        school_name = current_study.school.name if current_study and current_study.school else "-"
        level_name = current_study.level.name if current_study and current_study.level else "-"
        
        return download_result_pdf(
            students=[student],
            category_1_data=category_1_data,
            category_2_data=category_2_data,
            academic_year=int(selected_academic_year) + 543,
            student_name=f"{student.first_name}_{student.last_name}",
            school_name=school_name,
            level_name=level_name
        )

    subject_totals = {}
    if current_study and current_semester:
        subject_to_studies = SubjectToStudy.objects.filter(
            level=current_study.level,
            semester=current_semester.semester
        ).select_related('subject')
        subject_totals = {subject.subject.name: subject.subject.total_marks for subject in subject_to_studies}

    context = {
        'student': student,
        'current_study': current_study,
        'current_semester': current_semester,
        'selected_academic_year': selected_academic_year,
        'academic_years': academic_years,
        'subjects_cat1': subjects_cat1_data,
        'subjects_cat2': subjects_cat2_data,
        'subject_totals': subject_totals,
    }

    return render(request, 'student/student_results.html', context)

def download_result_pdf(students, category_1_data, category_2_data, academic_year, student_name, school_name, level_name):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student_name}_results_{academic_year}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'THSarabunNew'
    styles['Normal'].fontSize = 18

    title_style_header = ParagraphStyle(name='Title', fontName='THSarabunNew', fontSize=16, alignment=1)
    title_style_para = ParagraphStyle(name='Title', fontName='THSarabunNew', fontSize=16, alignment=0)
    sub_title_style = ParagraphStyle(name='SubTitle', fontName='THSarabunNew', fontSize=16, alignment=1)
    normal_style = ParagraphStyle(name='Normal', fontName='THSarabunNew', fontSize=16, alignment=0)

    logo_path = "static/images/logo.png"
    logo = Image(logo_path, width=80, height=80)
    logo.hAlign = 'CENTER'

    header = Paragraph("สมาคมคุรุสัมพันธ์อิสลามแห่งประเทศไทย ประจำหน่วยสอบที่ 80", title_style_header)
    school_name_paragraph = Paragraph(f"โรงเรียน {school_name}", sub_title_style)
    student_info = Paragraph(f"บันทึกผลการเรียนของ {student_name} {level_name}", normal_style)
    academic_year_text = Paragraph(f"ประจำปีการศึกษา {academic_year}", normal_style)

    table_data_cat1 = [['วิชา', 'คะแนน', 'เกรด', 'ผ่าน/ไม่ผ่าน']] + category_1_data
    table_data_cat2 = [['วิชา', 'คะแนน', 'เกรด', 'ผ่าน/ไม่ผ่าน']] + category_2_data

    # Handle empty data for Category 1 (Theoretical)
    if len(table_data_cat1) == 1:
        table_cat1 = Paragraph("\u0e22\u0e31\u0e07\u0e44\u0e21\u0e48\u0e21\u0e35\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25\u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a\u0e20\u0e32\u0e04\u0e17\u0e24\u0e28\u0e14\u0e35", sub_title_style)
    else:
        table_cat1 = Table(table_data_cat1, colWidths=[200, 100, 100, 100])
        table_cat1.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'THSarabunNew'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

    # Handle empty data for Category 2 (Practical)
    if len(table_data_cat2) == 1:
        table_cat2 = Paragraph("\u0e22\u0e31\u0e07\u0e44\u0e21\u0e48\u0e21\u0e35\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25\u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a\u0e20\u0e32\u0e04\u0e1b\u0e0f\u0e34\u0e1a\u0e31\u0e15\u0e34", sub_title_style)
    else:
        table_cat2 = Table(table_data_cat2, colWidths=[200, 100, 100, 100])
        table_cat2.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'THSarabunNew'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

    elements = [
        logo,
        Spacer(1, 10),
        header,
        Spacer(1, 20),
        school_name_paragraph,
        Spacer(1, 20),
        student_info,
        Spacer(1, 10),
        academic_year_text,
        Spacer(1, 20),
        Paragraph("ผลการศึกษาภาคทฤษฎี", title_style_para),
        Spacer(1, 20),
        table_cat1,
        Spacer(1, 15),
        Paragraph("ผลการศึกษาภาคปฏิบัติ", title_style_para),
        Spacer(1, 20),
        table_cat2
    ]

    doc.build(elements)

    return response

def student_Resultss(request, student_id):
     # Check if 'user_type' is in the session
    user_type = request.session.get('user_type')
    
    # If no user_type is found, redirect to login
    if not user_type:
        return redirect('login_view')  # Redirect to login if user_type is not in session
    
    # Get the student object
    student = get_object_or_404(Student, id=student_id)

    # Current study and semester
    current_study = CurrentStudy.objects.filter(student=student).first()
    current_semester = CurrentSemester.objects.first()

    # Fetch academic years and subjects
    academic_years = StudentHistory.objects.filter(student_id=student.id).values_list('academic_year', flat=True).distinct().order_by('-academic_year')
    # Determine the selected academic year
    selected_academic_year = request.GET.get('academic_year') or (academic_years.first() if academic_years else (current_semester.year if current_semester else None))
    # Fetch the relevant records
    subjects_sem1_instance = StudentHistory.objects.filter(student_id=student.id, semester=1, academic_year=selected_academic_year).first()
    subjects_sem2_instance = StudentHistory.objects.filter(student_id=student.id, semester=2, academic_year=selected_academic_year).first()

    # Call get_subject_data on single instances
    subjects_sem1_data = subjects_sem1_instance.get_subject_data() if subjects_sem1_instance else []
    subjects_sem2_data = subjects_sem2_instance.get_subject_data() if subjects_sem2_instance else []
    
    if 'download_pdf' in request.GET:
        # Prepare data for PDF
        semester_1_data = [
            (s['name'], s['marks'], s['grade'], s['status']) for s in subjects_sem1_data
        ]
        semester_2_data = [
            (s['name'], s['marks'], s['grade'], s['status']) for s in subjects_sem2_data
        ]
        
        # Pass the school name as well
        school_name = current_study.school.name if current_study and current_study.school else "-"
        level_name = current_study.level.name if current_study and current_study.level else "-"  # Assuming the level name is stored in current_study
        return download_result_pdf(
            students=[student],
            semester_1_data=semester_1_data,
            semester_2_data=semester_2_data,
            academic_year=int(selected_academic_year)+543,
            student_name=f"{student.first_name}_{student.last_name}",
            school_name=school_name,
            level_name=level_name
        )

    # Fetch subject totals (optional)
    subject_totals = {}
    if current_study and current_semester:
        subject_to_studies = SubjectToStudy.objects.filter(
            level=current_study.level,
            semester=current_semester.semester
        ).select_related('subject')
        subject_totals = {subject.subject.name: subject.subject.total_marks for subject in subject_to_studies}

    context = {
        'student': student,
        'current_study': current_study,
        'current_semester': current_semester,
        'selected_academic_year':selected_academic_year,
        'academic_years': academic_years,
        'subjects_sem1': subjects_sem1_data,
        'subjects_sem2': subjects_sem2_data,
        'subject_totals': subject_totals,
    }

    return render(request, 'student/student_results.html', context)

def download_result_pdfs(students, semester_1_data, semester_2_data, academic_year, student_name, school_name, level_name):
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student_name}_results_{academic_year}.pdf"'

# Document setup: Landscape A4 with margins
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    # Styles
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'THSarabunNew'
    styles['Normal'].fontSize = 18

    title_style = ParagraphStyle(
        name='Title',
        fontName='THSarabunNew',
        fontSize=16,
        alignment=1  # Center alignment
    )

    sub_title_style = ParagraphStyle(
        name='SubTitle',
        fontName='THSarabunNew',
        fontSize=16,
        alignment=1  # Center alignment
    )

    normal_style = ParagraphStyle(
        name='Normal',
        fontName='THSarabunNew',
        fontSize=16,
        alignment=0  # Left alignment
    )

    # Add logo
    logo_path = "static/images/logo.png"
    logo = Image(logo_path, width=80, height=80)  # Adjust size as needed
    logo.hAlign = 'CENTER'

    # Headings
    header = Paragraph("สมาคมคุรุสัมพันธ์อิสลามแห่งประเทศไทย ประจำหน่วยสอบที่ 80", title_style)
    school_name_paragraph = Paragraph(f"โรงเรียน {school_name}", sub_title_style)
    student_info = Paragraph(f"บันทึกผลการเรียนของ {student_name} {level_name}", normal_style)
    academic_year_text = Paragraph(f"ประจำปีการศึกษา {academic_year}", normal_style)

    # Table data for Semester 1 and Semester 2
    table_data_sem1 = [
        ['วิชา', 'คะแนน', 'เกรด', 'ผ่าน/ไม่ผ่าน']
    ] + semester_1_data

    table_data_sem2 = [
        ['วิชา', 'คะแนน', 'เกรด', 'ผ่าน/ไม่ผ่าน']
    ] + semester_2_data

    # Handle empty data for Semester 1
    if len(table_data_sem1) == 1:
        table_sem1 = Paragraph("ยังไม่มีข้อมูลสำหรับภาคการศึกษานี้", sub_title_style)
    else:
        table_sem1 = Table(table_data_sem1, colWidths=[200, 100, 100, 100])
        table_sem1.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'THSarabunNew'),  # Custom font
            ('FONTSIZE', (0, 0), (-1, -1), 14),  # Set font size to 16
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header row color
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center align for the header row
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Align first column (Subject) to the left
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Align other columns to the center
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Table grid
            ('TOPPADDING', (0, 0), (-1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

    # Handle empty data for Semester 2
    if len(table_data_sem2) == 1:
        table_sem2 = Paragraph("ยังไม่มีข้อมูลสำหรับภาคการศึกษานี้", sub_title_style)
    else:
        table_sem2 = Table(table_data_sem2, colWidths=[200, 100, 100, 100])
        table_sem2.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'THSarabunNew'),  # Custom font
            ('FONTSIZE', (0, 0), (-1, -1), 14),  # Set font size to 16
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header row color
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center align for the header row
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Align first column (Subject) to the left
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Align other columns to the center
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Table grid
            ('TOPPADDING', (0, 0), (-1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
    # Build the PDF with elements
    elements = [
        logo,
        Spacer(1, 10),  # Space below logo
        header,
        Spacer(1, 20),
        school_name_paragraph,
        Spacer(1, 20),
        student_info,
        Spacer(1, 10),
        academic_year_text,
        Spacer(1, 20),  # Space below academic year
        Paragraph(f"ผลการศึกษาภาคการศึกษาที่ 1", title_style),
        Spacer(1, 20),
        table_sem1,
        Spacer(1, 15),  # Space between tables
        Paragraph(f"ผลการศึกษาภาคการศึกษาที่ 2", title_style),
        Spacer(1, 20),
        table_sem2
    ]

    # Generate the document
    doc.build(elements)

    return response



