from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RoomSerializer,CreateRoomSerializer,UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
# Create your views here.          

#/Room  Views
class RoomView(generics.CreateAPIView):
    queryset = Room.objects.all()   #এটি নির্দেশ করছে যে এই API Room মডেলের ডেটাবেস থেকে সমস্ত রেকর্ড নিয়ে কাজ করবে।
    serializer_class = RoomSerializer

# /Get_Room views
class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwargs = 'code'

    def get(self, request, format=None):
        code = request.GET.get(self.lookup_url_kwargs)
        if code != None:
            room = Room.objects.filter(code = code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room code...'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad Request': 'Code parameter Not found in request'}, status = status.HTTP_400_BAD_REQUEST)
    
#/Join-Room 
class JoinRoom(APIView):
    lookup_url_kwarg = 'code'

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                self.request.session['room_code'] = code
                return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)

            return Response({'Bad Request': 'Invalid Room Code'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Bad Request': 'Invalid post data, did not find a code key'}, status=status.HTTP_400_BAD_REQUEST)







# /Create-Room Views
class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format = None):     # format will be used in handle json,xml etc 
        if not self.request.session.exists(self.request.session.session_key):   #ব্যবহারকারীর বর্তমান সেশনের জন্য ব্যবহার করা ইউনিক কী বা আইডেন্টিফায়ার। Django এটি ব্যবহার করে বুঝতে পারে যে কোন সেশনটি কোন ব্যবহারকারীর সাথে সম্পর্কিত।#self.request.session হল Django-তে সেশন ব্যবস্থাপনার জন্য ব্যবহৃত একটি অবজেক্ট, এবং এটি request অবজেক্টের অংশ।exists পদ্ধতি, যা সেশনের বর্তমান অবস্থা চেক করতে ব্যবহৃত হয়, সেটি session অবজেক্টের একটি পদ্ধতি। তাই self.request.session.exists(...) লেখার জন্য আপনাকে প্রথমে session অবজেক্টটি নির্দেশ করতে হবে।
             self.request.session.create()
    
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.guest_can_pause
            votes_to_skip = serializer.data.votes_to_skip
            host = self.request.session.session_key
            queryset = Room.objects.filter(host = host)   #এখানে, আমরা Room মডেলের filter() মেথড ব্যবহার করে সবার থেকে সেই রুমের তথ্য খুঁজে বের করছি যার হোস্ট হল বর্তমান ব্যবহারকারী (হোস্ট)।
            if queryset.exists():       #এই লাইনটি পরীক্ষা করে যে queryset এ কোন রুম আছে কি না। যদি থাকে, তাহলে আমরা সেই রুমের তথ্য নিয়ে কাজ করতে পারব।
                room = queryset[0]      #এটি queryset এর প্রথম রুমের তথ্য (যদি একাধিক রুম থাকে) নিয়ে আসছে।
                room.guest_can_pause = guest_can_pause  # guest_can_pause এবং votes_to_skip এর মানগুলি আপডেট করছি, যা আমরা সিরিয়ালাইজার থেকে উদ্ধার করেছি।
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])     #save() মেথডটি ব্যবহার করে আমরা পরিবর্তিত তথ্যটি (অর্থাৎ, guest_can_pause এবং votes_to_skip) সেভ করছি।
            else:  
                room = Room(host = host, guest_can_pause = guest_can_pause, votes_to_skip = votes_to_skip)       #indicates the value of if queryset .exists
                room.save()    
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)        #RoomSerializer হচ্ছে একটি সিরিয়ালাইজার, যা room অবজেক্টের ডেটাকে JSON ফরম্যাটে রূপান্তর করে। HTTP স্ট্যাটাস কোড 201 Created ব্যবহার করা হচ্ছে, যা নির্দেশ করে যে রিসোর্সটি (এই ক্ষেত্রে, রুম) সফলভাবে তৈরি হয়েছে।
        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)       ##Else

# /userinRoom Views 
class UserInRoom(APIView):
    def get(self, request, format = None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        data={
            'code':self.request.session.get('room_code')
        }
        return JsonResponse(data, status=status.HTTP_200_OK)


# /LeaveRoom views
class LeaveRoom(APIView):
    def post(self, request, format = None):
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code')
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host = host_id)
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()

        return Response({'Message':'Success'}, status=status.HTTP_200_OK)

# /update views

class UpdateView(APIView):
    serializer_class = UpdateRoomSerializer
    
    def patch(self, request, format = None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')
            
            queryset = Room.objects.filter(code = code)
            if not queryset.exists():
                return Response({'msg': 'Room not found'}, status = status.HTTP_404_NOT_FOUND)
            
            room = queryset[0]
            user_id = self.request.session.session_key
            if room.host != user_id:
                return Response({'msg': 'You are not the host of this room.'}, status=status.HTTP_403_FORBIDDEN)
            
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data, status = status.HTTP_200_OK)


        return Response({'Bad Request': 'Invalid data...'}, status = status.HTTP_400_BAD_REQUEST)
    






