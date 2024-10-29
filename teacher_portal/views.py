from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'teacher_portal/login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('login')
    
    return render(request, 'teacher_portal/register.html')

@login_required
def home_view(request):
    students = Student.objects.all()
    return render(request, 'teacher_portal/home.html', {'students': students})

@csrf_exempt
@login_required
def add_student(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        subject = data.get('subject')
        marks = data.get('marks')
        if name and subject and marks is not None:
            if Student.objects.filter(name=name, subject=subject).exists():
                student = Student.objects.get(name=name, subject=subject)
                student.marks = marks
                student.save()
                return JsonResponse({'status': 'success', 'message': 'Student updated successfully'})
            student = Student.objects.create(name=name, subject=subject, marks=marks)
            student.save()
            return JsonResponse({'status': 'success', 'message': 'Student added successfully'})
        else:
            return JsonResponse({'status': 'fail', 'message': 'All fields are required'})
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def edit_student(request, student_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        student = get_object_or_404(Student, id=student_id)
        student.name = data.get('name', student.name)
        student.subject = data.get('subject', student.subject)
        student.marks = data.get('marks', student.marks)
        student.save()
        return JsonResponse({'status': 'success', 'message': 'Student updated successfully'})
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def delete_student(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        student.delete()
        return JsonResponse({'status': 'success', 'message': 'Student deleted successfully'})
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'})


def logout_view(request):
    logout(request)
    return redirect('login')