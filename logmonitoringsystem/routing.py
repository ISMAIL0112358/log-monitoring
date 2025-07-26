# chat/routing.py
from django.urls import re_path

from .webhook_consumer import WebhookConsumer

websocket_urlpatterns = [
    re_path(r"ws/get-logs/", WebhookConsumer.as_asgi()),
]