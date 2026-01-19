from django.db import models
from django.contrib.auth.models import User
from quizzes.models import Quiz
from questions.models import Question

# Create your models here.

class QuizSession(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Players'),
        ('active', 'Active'),
        ('finished', 'Finished'),
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz.title} - {self.code}"

class Participant(models.Model):
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.session}"

class AnswerSubmission(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='submissions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey('questions.Answer', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participant', 'question')

    def __str__(self):
        return f"{self.participant} - {self.question}"
