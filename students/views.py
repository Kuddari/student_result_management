# students/views.py
import logging
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import StudentRegistrationForm
from .models import Student

# Create a logger
logger = logging.getLogger(__name__)

def student_registration(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.save()
            messages.success(request, "Student registered successfully!")
            return redirect('student_list')  # Redirect to the home page
        else:
            # Log form errors
            logger.error("Form errors: %s", form.errors)
    else:
        form = StudentRegistrationForm()
    
    return render(request, "students/student_registration.html", {'form': form})

def student_list(request):
    students = Student.objects.all()  # Retrieve all students
    return render(request, "students/student_list.html", {'students': students})

def student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, "students/student_profile.html", {'student': student})