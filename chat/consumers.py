import json

from typing import Optional, Dict

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name: Optional[str] = None
        self.room_group_name: Optional[str] = None

    def connect(self):
        """
        Join Room Group
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        """
        Leave room group
        """
        self._verify_state()

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        """
        Receive message from WebSocket and send message to group
        """
        self._verify_state()

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': self.chat_message.__name__,
                'message': message
            }
        )

    def chat_message(self, event: Dict[str, str]):
        """
        Receive message from Room Group and send it to WebSocket
        """
        self._verify_state()

        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))

    def _verify_state(self):
        """
        Utility function to make sure that state has been properly set up in call to `connect`
        """
        assert self.room_group_name is not None, 'Room Group Name is missing'
