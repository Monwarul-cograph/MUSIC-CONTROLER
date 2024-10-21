from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RoomSerializer,CreateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response

class RoomView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class=RoomSerializer

#create post method
class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format = None):
        if not self.request.session.exists(self.requests.session.session_key):
            
