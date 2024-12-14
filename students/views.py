# students/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.db.models import Q, F, FloatField, ExpressionWrapper
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login
from decimal import Decimal
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime  # Import the datetime module
from django.views.decorators.csrf import csrf_exempt
import json
from urllib.parse import urlencode

    
pdfmetrics.registerFont(TTFont('THSarabunNew', 'static/fonts/THSarabunNew.ttf'))

def login_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')     # User ID input
        password = request.POST.get('password') # Student's ID number or Teacher's password

        # Authenticate the user based on the provided user_id and id_number
        user = authenticate(request, username=user_id, password=password)

        if user is not None:
            login(request, user)
            # Set session data after login
            if Student.objects.filter(id=user_id).exists():
                request.session['user_type'] = 'student'
                request.session['student_id'] = user_id
            elif Teacher.objects.filter(id=user_id).exists():
                request.session['user_type'] = 'teacher'
                request.session['teacher_id'] = user_id
            return redirect('home')  # Redirect to home after successful login
        else:
            # Authentication failed
            return render(request, 'auth/login.html', {
                'error_message': 'ไอดีผู้ใช้หรือรหัสผ่านไม่ถูกต้อง',  # "Incorrect user ID or password"
            })

    return render(request, 'auth/login.html')

def student_login(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student_id_number = request.POST.get('student_id_number')

        user = authenticate(request, student_id=student_id, student_id_number=student_id_number)

        if user is not None:
            login(request, user)
            request.session['student_id'] = student_id
            return redirect('home')
        else:
            return render(request, 'auth/student_login.html', {
                'error_message': 'รหัสนักเรียนหรือเลขประจำตัวประชาชนไม่ถูกต้อง'
            })

    return render(request, 'auth/student_login.html')

def get_schools(request):
    schools = list(School.objects.values('id', 'name'))
    return JsonResponse(schools, safe=False)

def safe_int(value):
    """Convert a value to int or return 0 if it's not valid."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

@csrf_exempt
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
        students = Student.objects.all()
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
    
    if user_type == 'teacher' and 'teacher_id' in request.session:
        user_id = request.session['teacher_id']
        
        # Get teeacher data
        try:
            teacher = Teacher.objects.get(id=user_id)
        except Teacher.DoesNotExist:
            return redirect('login_view')  # Redirect if student not found

        # Get student statistics
        students = Student.objects.all()
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
    
    
def Homes(request):
    # Get student data
    # Check if 'student_id' is in the session
    if 'student_id' not in request.session:
        return redirect('student_login')

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
    return render(request, 'student_home.html', context)


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
        'schools': schools,
        'levels': levels,
        'academic_years': academic_years,
        'students': histories,
        'subjects': subjects,
        'subject_totals': subject_totals,
        'academic_year': academic_year,
        'current_semester': current_semester,
    }

    return render(request, 'student/gr_student.html')

def Student_Rp(request):
    # Check if 'user_type' is in the session
    user_type = request.session.get('user_type')
    
    # If no user_type is found, redirect to login
    if not user_type:
        return redirect('login_view')  # Redirect to login if user_type is not in session

    # If user is not a teacher, redirect to home
    if user_type == 'student':
        return redirect('home')  # Redirect student back to home

    # รับค่าฟิลเตอร์
    search = request.GET.get('search', '').strip()
    school = request.GET.get('school')
    level = request.GET.get('level')
    academic_year = request.GET.get('academic_year')
    gender = request.GET.get('gender')
    special_status = request.GET.get('special_status')
    action = request.GET.get('action')  # Check for download action
    print(f"special_status: {special_status}")  # Debugging
    print(f"gender: {gender}")  # Debugging

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

    # กรองตามเพศ
    if gender:
        students = students.filter(gender=gender)

    # กรองตามสถานะพิเศษ
    if special_status:
        students = students.filter(special_status=special_status)
    
    # Check if the action is to download the PDF
    if action == 'download':
        return download_students_pdf(students)

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
        'current_filters': {
            'search': search,
            'school': school,
            'level': level,
            'academic_year': academic_year,
            'gender': gender,
            'special_status': special_status,
        },
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
    info_paragraph = Paragraph(header_info, styles['Normal'])

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


def edit_Profile(request):
    return render(request, 'edit/edit_profile.html')

def student_Results(request):
    subjects_sem1 = [
        {'id': 1, 'name': 'รายวิชา 1', 'teacher': 'ชื่อผู้สอน 1', 'score': 100, 'grade': 4, 'status': 'ผ่าน'},
        {'id': 2, 'name': 'รายวิชา 2', 'teacher': 'ชื่อผู้สอน 2', 'score': 100, 'grade': 4, 'status': 'ผ่าน'},
        {'id': 3, 'name': 'รายวิชา 3', 'teacher': 'ชื่อผู้สอน 3', 'score': 45, 'grade': 0, 'status': 'ไม่ผ่าน'},
        {'id': 4, 'name': 'รายวิชา 4', 'teacher': 'ชื่อผู้สอน 4', 'score': 85, 'grade': 4, 'status': 'ผ่าน'},
        {'id': 5, 'name': 'รายวิชา 5', 'teacher': 'ชื่อผู้สอน 5', 'score': 55, 'grade': 1, 'status': 'ผ่าน'},
    ]

    subjects_sem2 = [
        {'id': 1, 'name': 'รายวิชา 1', 'teacher': 'ชื่อผู้สอน 1', 'score': 100, 'grade': 4, 'status': 'ผ่าน'},
        {'id': 2, 'name': 'รายวิชา 2', 'teacher': 'ชื่อผู้สอน 2', 'score': 70, 'grade': 2, 'status': 'ผ่าน'},
        {'id': 3, 'name': 'รายวิชา 3', 'teacher': 'ชื่อผู้สอน 3', 'score': 45, 'grade': 0, 'status': 'ไม่ผ่าน'},
        {'id': 4, 'name': 'รายวิชา 4', 'teacher': 'ชื่อผู้สอน 4', 'score': 85, 'grade': 4, 'status': 'ผ่าน'},
        {'id': 5, 'name': 'รายวิชา 5', 'teacher': 'ชื่อผู้สอน 5', 'score': 55, 'grade': 1, 'status': 'ผ่าน'},
    ]

    return render(request, 'student/student_results.html', {
        'subjects_sem1': subjects_sem1,
        'subjects_sem2': subjects_sem2,
    })


def in_Profile(request, student_id=None):
    provinces = Province.objects.all()
    schools = School.objects.all()
    levels = Level.objects.all()
    # Check if editing an existing student
    student = None
    father = None
    mother = None
    guardian = None
    current_study = None

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
        # Handle Student Data
        student_profile_pic = request.FILES.get('profile_picture')
        if student_profile_pic:
            student.profile_picture = student_profile_pic
        student_first_name = request.POST.get('student-first-name')
        student_last_name = request.POST.get('student-last-name')
        student_english_first_name = request.POST.get('student-english-first-name')
        student_english_last_name = request.POST.get('student-english-last-name')
        student_arabic_first_name = request.POST.get('student-arabic-first-name')
        student_arabic_last_name = request.POST.get('student-arabic-last-name')
        student_dob =  parse_date(request.POST.get('student-dob'))
        # Get the Thai ID number from the form
        student_id_number = request.POST.get('student-id-number', '').replace(' ', '')
        # Validate the Thai ID number (should be exactly 13 digits)
        if not student_id_number.isdigit() or len(student_id_number) != 13:
            return JsonResponse({'error': 'Invalid Thai ID number. It must contain exactly 13 digits.'}, status=400)
        school_id = request.POST.get('student-school')
        level_id = request.POST.get('student-level')
        level = Level.objects.get(id=level_id) if level_id else None

        special_status = request.POST.get('special-status')
        gender = request.POST.get('gender')  # Add this line to handle gender

        student_school = None
        if school_id:
            student_school = get_object_or_404(School, id=school_id)

        # Create or update student
        if student:
            student.profile_picture = student_profile_pic
            student.first_name = student_first_name
            student.last_name = student_last_name
            student.english_first_name = student_english_first_name
            student.english_last_name = student_english_last_name
            student.arabic_first_name = student_arabic_first_name
            student.arabic_last_name = student_arabic_last_name
            student.date_of_birth = student_dob  # Add this line
            student.id_number = student_id_number  # Add this line
            student.special_status = special_status
            student.gender = gender
            student.save()
        else:
            student = Student.objects.create(
                first_name=student_first_name,
                last_name=student_last_name,
                english_first_name=student_english_first_name,
                english_last_name=student_english_last_name,
                arabic_first_name=student_arabic_first_name,
                arabic_last_name=student_arabic_last_name,
                date_of_birth=student_dob,  # Add this line
                id_number=student_id_number,  # Add this line
                special_status=special_status,
                gender = gender
            )

        # Create or update CurrentStudy
        if current_study:
            current_study.student = student
            current_study.school = student_school
            current_study.level = level  # Update the level
            current_study.save()
        else:
            if student_school:
                CurrentStudy.objects.create(
                    student=student,
                    school=student_school,
                    level=level  # Set the level when creating the record
                )

         # Function to handle address creation or update
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
            address, created = Address.objects.update_or_create(
                house_number=address_data['house_number'],
                street=address_data['street'],
                moo=address_data['moo'],
                defaults=address_data
            )
            return address

        # Handle Father Data
        father_address = handle_address('father')
        father_data = {
            'first_name': request.POST.get('father-first-name'),
            'last_name': request.POST.get('father-last-name'),
            'date_of_birth':  parse_date(request.POST.get('father-dob')),
            'phone_number': request.POST.get('father-phone'),
            'occupation': request.POST.get('father-occupation'),
            'workplace': request.POST.get('father-workplace'),
            'income': safe_int(request.POST.get('father-income')),
            'address': father_address,
        }
        Father.objects.update_or_create(student=student, defaults=father_data)

        # Handle Mother Data
        mother_address = handle_address('mother')
        mother_data = {
            'first_name': request.POST.get('mother-first-name'),
            'last_name': request.POST.get('mother-last-name'),
            'date_of_birth':  parse_date(request.POST.get('mother-dob')),
            'phone_number': request.POST.get('mother-phone'),
            'occupation': request.POST.get('mother-occupation'),
            'workplace': request.POST.get('mother-workplace'),
            'income': safe_int(request.POST.get('mother-income')),
            'address': mother_address,
        }
        Mother.objects.update_or_create(student=student, defaults=mother_data)

        
        guardian_address = handle_address('guardian')
        guardian_data = {
            'relationship_with_student': request.POST.get('relationship'), # Save relationship
            'first_name': request.POST.get('guardian-first-name'),
            'last_name': request.POST.get('guardian-last-name'),
            'date_of_birth': parse_date(request.POST.get('guardian-dob')),
            'phone_number': request.POST.get('guardian-phone'),
            'occupation': request.POST.get('guardian-occupation'),
            'workplace': request.POST.get('guardian-workplace'),
            'income': safe_int(request.POST.get('guardian-income')),
            'address': guardian_address,
        }

        Guardian.objects.update_or_create(student=student, defaults=guardian_data)


        return redirect('profile', student_id=student.id)# Redirect to a success page after submission

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

def Profile(request, student_id):
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


def student_marks_view(request):
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
                student_name=f"{student.student.first_name} {student.student.last_name}",
                school_name=student.school.name,
                level_name=student.level.name,
                semester=f"{current_semester.semester} - {current_semester.year}",
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
        'schools': schools,
        'levels': levels,
        'students': students,
        'subjects': subjects,
        'current_semester': current_semester,
        'student_marks_data': student_marks_data,
    }

    return render(request, 'inputdata/ingr_student.html', context)


