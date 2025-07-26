import datetime
import json

from asgiref.sync import async_to_sync
from rest_framework.response import Response
from rest_framework.views import APIView


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

