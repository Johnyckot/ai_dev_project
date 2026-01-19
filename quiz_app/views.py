from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from quizzes.models import Quiz
from questions.models import Question, Answer

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def quiz_list(request):
    quizzes = Quiz.objects.filter(created_by=request.user)
    return render(request, 'quiz_list.html', {'quizzes': quizzes})

def create_quiz(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        quiz = Quiz.objects.create(title=title, description=description, created_by=request.user)
        return redirect('quiz_detail', quiz_id=quiz.id)
    return render(request, 'create_quiz.html')

def quiz_detail(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.questions.all()
    return render(request, 'quiz_detail.html', {'quiz': quiz, 'questions': questions})