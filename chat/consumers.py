import json
from shlex import quote

from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = quote(text_data_json['message'])

        self.send(text_data=json.dumps({
            'message': message
        }))
