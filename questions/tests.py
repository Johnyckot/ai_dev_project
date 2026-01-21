from django.test import TestCase
from .models import Question, Answer
from quizzes.models import Quiz
from django.contrib.auth.models import User

class QuestionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="creator", password="pass")
        self.quiz = Quiz.objects.create(title="Test Quiz", description="Test", created_by=self.user)

    def test_question_creation(self):
        question = Question.objects.create(
            quiz=self.quiz,
            text="What is 2+2?",
            question_type="multiple_choice"
        )
        self.assertEqual(question.text, "What is 2+2?")
        self.assertEqual(question.question_type, "multiple_choice")

class AnswerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="creator", password="pass")
        self.quiz = Quiz.objects.create(title="Test Quiz", description="Test", created_by=self.user)
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="What is 2+2?",
            question_type="multiple_choice"
        )

    def test_answer_creation(self):
        answer = Answer.objects.create(
            question=self.question,
            text="4",
            is_correct=True
        )
        self.assertEqual(answer.text, "4")
        self.assertTrue(answer.is_correct)
