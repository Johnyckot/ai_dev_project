from django.test import TestCase
from django.contrib.auth.models import User
from quizzes.models import Quiz
from questions.models import Question, Answer
from .models import QuizSession, Participant, AnswerSubmission

class QuizSessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="host", password="pass")
        self.quiz = Quiz.objects.create(title="Test Quiz", description="Test", created_by=self.user)

    def test_quiz_session_creation(self):
        session = QuizSession.objects.create(quiz=self.quiz, host=self.user)
        self.assertEqual(session.quiz, self.quiz)
        self.assertEqual(session.host, self.user)
        self.assertEqual(session.status, "waiting")

class ParticipantTestCase(TestCase):
    def setUp(self):
        self.host = User.objects.create_user(username="host", password="pass")
        self.quiz = Quiz.objects.create(title="Test Quiz", description="Test", created_by=self.host)
        self.session = QuizSession.objects.create(quiz=self.quiz, host=self.host)
        self.user = User.objects.create_user(username="participant", password="pass")

    def test_participant_creation(self):
        participant = Participant.objects.create(session=self.session, user=self.user)
        self.assertEqual(participant.session, self.session)
        self.assertEqual(participant.user, self.user)
        self.assertEqual(participant.score, 0)

class AnswerSubmissionTestCase(TestCase):
    def setUp(self):
        self.host = User.objects.create_user(username="host", password="pass")
        self.quiz = Quiz.objects.create(title="Test Quiz", description="Test", created_by=self.host)
        self.question = Question.objects.create(quiz=self.quiz, text="Q?", question_type="mc")
        self.answer = Answer.objects.create(question=self.question, text="A", is_correct=True)
        self.session = QuizSession.objects.create(quiz=self.quiz, host=self.host)
        self.participant = Participant.objects.create(session=self.session, user=User.objects.create_user("part"))

    def test_answer_submission(self):
        submission = AnswerSubmission.objects.create(
            participant=self.participant,
            question=self.question,
            answer=self.answer
        )
        self.assertEqual(submission.participant, self.participant)
        self.assertEqual(submission.answer, self.answer)
