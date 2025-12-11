from django.urls import path

from logmonitoringsystem.logmonitoringsystem.webhook_consumer import WebhookConsumer

websocket_urlpatterns = [path(r"^ws/get-logs/", WebhookConsumer)]
