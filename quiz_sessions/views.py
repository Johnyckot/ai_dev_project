from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import QuizSession, Participant, AnswerSubmission
from questions.models import Answer
from .serializers import QuizSessionSerializer, ParticipantSerializer
import random
import string

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
        session.save()
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
        # Check if all participants have answered
        total_participants = session.participants.count()
        answered = AnswerSubmission.objects.filter(participant__session=session, question=question).count()
        if answered == total_participants:
            # All answered, move to next or finish
            next_question = session.quiz.questions.filter(id__gt=question.id).first()
            if next_question:
                session.current_question = next_question
                session.save()
            else:
                session.status = 'finished'
                session.save()
        return Response({'status': 'submitted'})

    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        session = self.get_object()
        participants = session.participants.order_by('-score')
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)
