import json

from logging import getLogger
from typing import Optional, Dict

from channels.auth import login
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name: Optional[str] = None
        self.room_group_name: Optional[str] = None
        self.user: Optional[User] = None
        self.logger = getLogger(f'{__name__}.{__class__.__qualname__}')

    async def connect(self):
        """
        Join Room Group
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
        except OSError as o_err:
            self.logger.error(f'Failed to connect to channel {self.channel_name}, is redis available?')
            raise o_err

        await self.accept()

    async def disconnect(self, code):
        """
        Leave room group
        """
        self._verify_state()

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Receive message from WebSocket and send message to group
        """
        self._verify_state()

        # login the user to this session.
        await login(self.scope, self._get_user_from_scope())
        # save the session (if the session backend does not access the db you can use `sync_to_async`)
        await database_sync_to_async(self.scope["session"].save)()

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': self.chat_message.__name__,
                'message': message
            }
        )

    async def chat_message(self, event: Dict[str, str]):
        """
        Receive message from Room Group and send it to WebSocket
        """
        self._verify_state()

        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    def _verify_state(self):
        """
        Utility function to make sure that state has been properly set up in call to `connect`
        """
        assert self.room_group_name is not None, 'Room Group Name is missing'
        assert self.user is not None, 'User needs to login'

    def _get_user_from_scope(self) -> User:
        return User.objects.get(id=int(self.scope["query_string"]))
