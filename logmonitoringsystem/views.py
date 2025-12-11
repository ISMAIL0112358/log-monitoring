import datetime
import json
import asyncio
import logging
import os
import time

from django.http import StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

logger = logging.getLogger('logmonitoringsystem')

class addlogs(APIView):
    def post(self, request):
        data = json.loads(request.body)
        log_message = data.get('logs')
        
        if not log_message:
            return Response({"error": "Bad Request", "message": "string is missing"},
                            status=400)
        
        logger.info(log_message)
        
        return Response({"message": "log appended to file"}, status=200)


class getlogs(APIView):

    def get(self, request):
        log_file_path = os.path.join(settings.BASE_DIR, 'log.txt')
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as file:
                logs = file.read()
        else:
            logs = ""
        return Response({"logs": logs}, status=200)


from django.shortcuts import render

def logs_view(request):
    return render(request, "logs.html")


def sse_logs(request):
    """
    Handles the SSE connection and streams new log lines to the client.
    """
    def event_stream():
        log_file_path = os.path.join(settings.BASE_DIR, 'log.txt')
        
        # Ensure file exists
        if not os.path.exists(log_file_path):
            open(log_file_path, 'a').close()

        with open(log_file_path, 'r') as f:
            # Move to the end of the file to only read new logs
            f.seek(0, os.SEEK_END)
            
            while True:
                line = f.readline()
                if line:
                    # Clean the line and yield it
                    yield f"data: {json.dumps({'log': line.strip()})}\n\n"
                else:
                    # No new line, wait a bit
                    time.sleep(0.1)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response['Cache-Control'] = 'no-cache'
    return response
