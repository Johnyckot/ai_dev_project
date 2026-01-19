from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import QuizSession, Participant
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

    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        session = self.get_object()
        participants = session.participants.order_by('-score')
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)
