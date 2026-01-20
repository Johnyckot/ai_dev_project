import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import QuizSession, Participant

class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_code = self.scope['url_route']['kwargs']['session_code']
        self.room_group_name = f'quiz_{self.session_code}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (not used for now)
    async def receive(self, text_data):
        pass

    # Send message to WebSocket
    async def quiz_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'quiz_started',
            'question': event['question']
        }))

    async def next_question(self, event):
        await self.send(text_data=json.dumps({
            'type': 'next_question',
            'question': event['question']
        }))

    async def quiz_finished(self, event):
        await self.send(text_data=json.dumps({
            'type': 'quiz_finished',
            'leaderboard': event['leaderboard']
        }))