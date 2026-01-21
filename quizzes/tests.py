from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Quiz

# Unit tests
class QuizTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="creator", password="pass")

    def test_quiz_creation(self):
        quiz = Quiz.objects.create(title="Test Quiz", description="A test quiz", created_by=self.user)
        self.assertEqual(quiz.title, "Test Quiz")
        self.assertEqual(quiz.description, "A test quiz")

# Integration tests
class QuizAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_authenticate(user=self.user)

    def test_create_quiz(self):
        url = reverse('quiz-list')
        data = {'title': 'New Quiz', 'description': 'Description'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Quiz.objects.get().title, 'New Quiz')

    def test_list_quizzes(self):
        Quiz.objects.create(title="Quiz 1", description="Desc 1", created_by=self.user)
        Quiz.objects.create(title="Quiz 2", description="Desc 2", created_by=self.user)
        url = reverse('quiz-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
