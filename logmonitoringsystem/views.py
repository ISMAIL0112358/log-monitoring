import datetime
import json
import asyncio

from asgiref.sync import async_to_sync
from django.http import StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from channels.layers import get_channel_layer


class addlogs(APIView):
    def post(self, request):
        data = json.loads(request.body)
        string = f"{datetime.datetime.now()} - {data.get('logs')} \n\n"
        if not string:
            return Response({"error": "Bad Request", "message": "string is missing"},
                            status=400)
        with open('log.txt', 'a') as file:
            file.write(string)
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()

        print("----------------------- sending logs")
        async_to_sync(channel_layer.group_send)(
            "log_room",
            {
                "type": "send_new_logs",
                "message": string  # Ensure this is a string
            }
        )

        print(" ------------------------ logs send")
        return Response({"message": "log appended to file"}, status=200)


class getlogs(APIView):

    def get(self, request):
        with open('log.txt', 'r') as file:
            logs = file.read()
        return Response({"logs": logs}, status=200)


from django.shortcuts import render

def logs_view(request):
    return render(request, "logs.html")  # Make sure logs.html is inside a templates folder


async def sse_logs(request):
    """
    Handles the SSE connection and streams log events to the client.
    """
    channel_layer = get_channel_layer()

    # Each client needs a unique channel to receive messages from the group.
    channel_name = await channel_layer.new_channel()
    await channel_layer.group_add("log_room", channel_name)

    async def event_stream():
        """A generator that yields SSE-formatted log messages."""
        try:
            while True:
                # Wait for a message on the client-specific channel
                message = await channel_layer.receive(channel_name)

                if message.get("type") == "send_new_logs":
                    log_data = message.get("message", "No log message received")
                    # Format the message as a Server-Sent Event
                    yield f"data: {json.dumps({'log': log_data})}\n\n"

                await asyncio.sleep(0.1)
        finally:
            # Clean up the channel from the group when the client disconnects
            await channel_layer.group_discard("log_room", channel_name)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'  # Ensure clients don't cache the stream
    return response
