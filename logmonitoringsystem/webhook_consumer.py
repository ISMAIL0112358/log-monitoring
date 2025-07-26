from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

class WebhookConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "log_room"  # Ensure this matches the APIView
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name  # Don't override this manually
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    def receive(self, text_data):
        print(f"------------- Received: {text_data}")
        self.send(text_data=text_data)

    def send_new_logs(self, event):
        message = event.get("message", "No logs received")
        print(f"i m getting logs: {message}")
        self.send(text_data=json.dumps({"log": message}))
