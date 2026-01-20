from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import QuizSession, Participant, AnswerSubmission
from questions.models import Answer
from .serializers import QuizSessionSerializer, ParticipantSerializer
import random
import string
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

class QuizSessionViewSet(viewsets.ModelViewSet):
    queryset = QuizSession.objects.all()
    serializer_class = QuizSessionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'join']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        serializer.save(host=self.request.user, code=code)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        session = self.get_object()
        user = request.user
        if not Participant.objects.filter(session=session, user=user).exists():
            Participant.objects.create(session=session, user=user)
        return Response({'status': 'joined'})

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        session = self.get_object()
        if session.host != request.user:
            return Response({'error': 'Only host can start'}, status=403)
        session.status = 'active'
        session.current_question = session.quiz.questions.first()
        session.current_question_start = timezone.now()
        session.save()
        # Send WebSocket message
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'quiz_{session.code}',
            {
                'type': 'quiz_started',
                'question': {
                    'id': session.current_question.id,
                    'text': session.current_question.text,
                    'answers': list(session.current_question.answers.values('id', 'text'))
                }
            }
        )
        return Response({'status': 'started'})

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        session = self.get_object()
        if session.status != 'active':
            return Response({'error': 'Session not active'}, status=400)
        question = session.current_question
        if not question:
            return Response({'error': 'No current question'}, status=400)
        answer_id = request.data.get('answer_id')
        if not answer_id:
            return Response({'error': 'Answer ID required'}, status=400)
        participant = Participant.objects.get(session=session, user=request.user)
        # Check if already submitted
        if AnswerSubmission.objects.filter(participant=participant, question=question).exists():
            return Response({'error': 'Already submitted'}, status=400)
        AnswerSubmission.objects.create(participant=participant, question=question, answer_id=answer_id)
        # Calculate score if correct
        answer = Answer.objects.get(id=answer_id)
        if answer.is_correct:
            participant.score += 10  # Example points
            participant.save()
        # Check if all participants have answered or timeout
        total_participants = session.participants.count()
        answered = AnswerSubmission.objects.filter(participant__session=session, question=question).count()
        time_elapsed = (timezone.now() - session.current_question_start).total_seconds()
        timeout = 30  # seconds
        channel_layer = get_channel_layer()
        moved = False
        if answered == total_participants or time_elapsed >= timeout:
            moved = True
            # All answered or timeout, move to next or finish
            next_question = session.quiz.questions.filter(id__gt=question.id).first()
            if next_question:
                session.current_question = next_question
                session.current_question_start = timezone.now()
                session.save()
                async_to_sync(channel_layer.group_send)(
                    f'quiz_{session.code}',
                    {
                        'type': 'next_question',
                        'question': {
                            'id': next_question.id,
                            'text': next_question.text,
                            'answers': list(next_question.answers.values('id', 'text'))
                        }
                    }
                )
            else:
                session.status = 'finished'
                session.save()
                # Get leaderboard
                participants = session.participants.order_by('-score')
                leaderboard = [{'username': p.user.username, 'score': p.score} for p in participants]
                async_to_sync(channel_layer.group_send)(
                    f'quiz_{session.code}',
                    {
                        'type': 'quiz_finished',
                        'leaderboard': leaderboard
                    }
                )
        return Response({'status': f'submitted, answered {answered}/{total_participants}, time {time_elapsed:.1f}s, moved: {moved}'})

    @action(detail=True, methods=['post'])
    def force_next(self, request, pk=None):
        session = self.get_object()
        if session.host != request.user:
            return Response({'error': 'Only host can force next'}, status=403)
        if session.status != 'active' or not session.current_question:
            return Response({'error': 'No active question'}, status=400)
        channel_layer = get_channel_layer()
        # Move to next or finish
        next_question = session.quiz.questions.filter(id__gt=session.current_question.id).first()
        if next_question:
            session.current_question = next_question
            session.current_question_start = timezone.now()
            session.save()
            async_to_sync(channel_layer.group_send)(
                f'quiz_{session.code}',
                {
                    'type': 'next_question',
                    'question': {
                        'id': next_question.id,
                        'text': next_question.text,
                        'answers': list(next_question.answers.values('id', 'text'))
                    }
                }
            )
        else:
            session.status = 'finished'
            session.save()
            participants = session.participants.order_by('-score')
            leaderboard = [{'username': p.user.username, 'score': p.score} for p in participants]
            async_to_sync(channel_layer.group_send)(
                f'quiz_{session.code}',
                {
                    'type': 'quiz_finished',
                    'leaderboard': leaderboard
                }
            )
        return Response({'status': 'next_forced'})
