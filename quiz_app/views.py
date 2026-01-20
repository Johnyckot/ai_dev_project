from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from quizzes.models import Quiz
from questions.models import Question, Answer
from quiz_sessions.models import QuizSession, Participant
import random
import string

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

def add_question(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    if request.method == 'POST':
        text = request.POST['text']
        question_type = request.POST['question_type']
        time_limit = request.POST.get('time_limit', 30)
        question = Question.objects.create(quiz=quiz, text=text, question_type=question_type, time_limit=time_limit)
        # Add answers
        answers_data = request.POST.getlist('answers')
        correct_index = int(request.POST.get('correct', 0))
        for i, ans_text in enumerate(answers_data):
            is_correct = (i == correct_index)
            Answer.objects.create(question=question, text=ans_text, is_correct=is_correct)
        return redirect('quiz_detail', quiz_id=quiz.id)
    return render(request, 'add_question.html', {'quiz': quiz})

def start_session(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    if request.method == 'POST':
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        session = QuizSession.objects.create(quiz=quiz, host=request.user, code=code)
        return redirect('session_detail', session_id=session.id)
    return render(request, 'start_session.html', {'quiz': quiz})

def session_detail(request, session_id):
    session = QuizSession.objects.get(id=session_id)
    participants = session.participants.all()
    return render(request, 'session_detail.html', {'session': session, 'participants': participants})

def join_session(request):
    if request.method == 'POST':
        code = request.POST['code']
        try:
            session = QuizSession.objects.get(code=code)
            if not Participant.objects.filter(session=session, user=request.user).exists():
                Participant.objects.create(session=session, user=request.user)
            return redirect('session_detail', session_id=session.id)
        except QuizSession.DoesNotExist:
            messages.error(request, 'Invalid session code')
    return render(request, 'join_session.html')