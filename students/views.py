# students/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.db.models import Q
from django.contrib import messages
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
    gender = request.GET.get('gender')
    special_status = request.GET.get('special_status')
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


def download_students_pdf(request):
    # รับค่าฟิลเตอร์
    search = request.GET.get('search', '').strip()
    school = request.GET.get('school')
    level = request.GET.get('level')
    academic_year = request.GET.get('academic_year')
    gender = request.GET.get('gender')
    special_status = request.GET.get('special_status')

    # Query นักเรียนเริ่มต้น
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

    # **กรองตามเพศและสถานะพิเศษ หลังจากการกรองเบื้องต้น**
    # กรองตามเพศ
    if gender:
        students = students.filter(gender__iexact=gender)

    # กรองตามสถานะพิเศษ
    if special_status:
        students = students.filter(special_status__iexact=special_status)

    # ตรวจสอบจำนวนผลลัพธ์หลังจากกรอง
    print(f"Filtered students count: {students.count()}")

    # หากไม่มีข้อมูลนักเรียนในผลลัพธ์ ให้แสดงข้อความ "ไม่มีข้อมูล"
    if not students.exists():
        student_data = [['ไม่มีข้อมูล']]
    else:
        # เตรียมข้อมูลสำหรับ PDF
        student_data = [
            ['ลำดับ', 'ชื่อ', 'นามสกุล', 'เพศ', 'โรงเรียน', 'สถานะพิเศษ'],  # หัวตาราง
        ]
        for i, student in enumerate(students, start=1):
            student_data.append([
                i,
                student.first_name,
                student.last_name,
                student.gender,
                student.current_study.school.name if student.current_study else 'ไม่มีข้อมูล',
                student.special_status or 'ไม่มีข้อมูล',
            ])
    # กำหนดค่าหัวข้อ
    school_name = School.objects.get(id=school).name if school else "ทุกโรงเรียน"
    level_name = Level.objects.get(id=level).name if level else "ทุกชั้น"
    academic_year_text = academic_year if academic_year else "ทุกปี"
    gender_text = gender if gender else "ทุกเพศ"
    status_text = special_status if special_status else "ทุกสถานะพิเศษ"
    header_info = f"ชั้น: {level_name} | ปีการศึกษา: {academic_year_text} | เพศ: {gender_text} | สถานะพิเศษ: {status_text}"

    # สร้าง Response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="students_report_{academic_year or "all"}.pdf"'

    # สร้าง PDF Document (A4 ขนาดแนวนอน)
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    # โลโก้
    logo_path = "static/images/logo.png"  # แก้ไขเป็น path ของโลโก้
    logo = Image(logo_path, width=1 * inch, height=1 * inch)

    # ชื่อโรงเรียน
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'THSarabunNew'
    styles['Normal'].fontSize = 20
    styles['Normal'].alignment = 1
    school_paragraph = Paragraph(f"<b>{school_name}</b>", styles['Normal'])

    # ข้อมูลจำนวนนักเรียน
    info_paragraph = Paragraph(header_info, styles['Normal'])

    # สร้าง Header Layout (ปรับ colWidths ให้ตรงกับ Table)
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

    # เพิ่มระยะห่างระหว่าง Header กับตาราง
    spacer = Spacer(1, 0.3 * inch)

    # สร้างตาราง
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

    # เพิ่มองค์ประกอบทั้งหมดลงใน PDF
    elements = [header_table, spacer, table]
    doc.build(elements)

    return response



def GR_Student (request):
    return render(request, 'inputdata/ingr_student.html')

def student_marks_view(request):
    """
    Handle rendering and submission of the student marks form.
    """
    # Get current semester
    current_semester = CurrentSemester.objects.first()

    if not current_semester:
        return render(request, 'inputdata/ingr_student.html', {'error': 'Current semester not set.'})

    # Filters from the GET request
    school_name = request.GET.get('school')
    level_name = request.GET.get('level')

    # Fetch filter options
    schools = School.objects.all()
    levels = Level.objects.all()

    students = []
    subjects = []

    if request.method == 'POST':
        # Handle form submission
        level_name = request.POST.get('level')

        # Query for the relevant students and subjects
        students = CurrentStudy.objects.filter(level__name=level_name, current_semester=current_semester)
        subjects = SubjectToStudy.objects.filter(level__name=level_name, semester=current_semester.semester)

        if not students.exists():
            return render(request, 'inputdata/ingr_student.html', {
                'error': 'No students found.',
                'schools': schools,
                'levels': levels,
            })

        if not subjects.exists():
            return render(request, 'inputdata/ingr_student.html', {
                'error': 'No subjects found.',
                'schools': schools,
                'levels': levels,
            })

        # Process and save marks
        for student in students:
            for subject in subjects:
                field_name = f"marks_{student.student.id}_{subject.subject.id}"
                marks = request.POST.get(field_name)

                if marks and marks.strip():
                    try:
                        marks = int(marks)
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

        return HttpResponseRedirect(reverse('gr_student'))

    # Handle GET request - render the form
    if school_name or level_name:
        students_query = CurrentStudy.objects.filter(current_semester=current_semester)

        if school_name:
            school_name = school_name.strip()
            students_query = students_query.filter(school__name__iexact=school_name)

        if level_name:
            level_name = level_name.strip()
            students_query = students_query.filter(level__name__iexact=level_name)

        students = students_query.select_related('student', 'level')

        if level_name:
            subjects = SubjectToStudy.objects.filter(
                level__name__iexact=level_name,
                semester=current_semester.semester,
            ).select_related('subject')

    context = {
        'schools': schools,
        'levels': levels,
        'students': students,
        'subjects': subjects,
        'current_semester': current_semester,
    }

    return render(request, 'inputdata/ingr_student.html', context)