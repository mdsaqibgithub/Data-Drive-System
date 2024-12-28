from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, UserAuthSerializer, LoginSerializer, FolderSerializer, FileSerializer
from .models import *
from .utils import get_tokens_for_user

# Create your views here.





class RegisterAPIView(APIView):
    permission_classes = [AllowAny]  # Override the global permission

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            user_serializer = UserAuthSerializer(user)
            response_data = {
                'user': user_serializer.data,
                'token': token
            }
            return Response(response_data ,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class LoginAPIView(APIView):
    permission_classes = [AllowAny]  # Override the global permission
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                # Generate tokens for the authenticated user
                tokens = get_tokens_for_user(user)
                user_serializer = UserAuthSerializer(user)
                return Response({
                    "message": "Login successful",
                    "user": user_serializer.data,
                    "tokens": tokens
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create Folder API
class FolderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        folder = Folder.objects.filter(owner=request.user, parent=None)
        serializer = FolderSerializer(folder, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response({"message": "Folder created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def put(self, request, folder_id):
        try:
            folder = Folder.objects.get(id=folder_id, owner=request.user)
        except Folder.DoesNotExist:
            return Response({"error": "Folder not found"}, status=status.HTTP_404_NOT_FOUND)
        
        folder.name = request.data.get('name', folder.name)
        parent_id = request.data.get('parent')
        if parent_id:
            try:
                parent_folder = Folder.objects.get(id=parent_id, owner=request.user)
            except Folder.DoesNotExist:
                return Response({"error": "Parent folder not found"}, status=status.HTTP_404_NOT_FOUND)
        
        folder.save()
        return Response({"message": "Folder updated successfully"}, status=status.HTTP_200_OK)
    

    def delete(self, request, folder_id):
        try:
            folder = Folder.objects.get(id=folder_id, owner=request.user)
        except Folder.DoesNotExist:
            return Response({"error": "Folder not found"}, status=status.HTTP_404_NOT_FOUND)
        
        folder.delete()
        return Response({"message": "Folder deleted successfully"}, status=status.HTTP_200_OK)



# Create File API
class FileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, folder_id=None, file_id=None):
    
        if file_id:
            try:
                folder = Folder.objects.get(id=folder_id, owner=request.user) if folder_id else None
                file = File.objects.get(id=file_id, folder=folder, owner=request.user) if folder else File.objects.get(id=file_id, owner=request.user)
            except (File.DoesNotExist, Folder.DoesNotExist):
                return Response({"error": "File or Folder not found"}, status=status.HTTP_404_NOT_FOUND)

           
            serializer = FileSerializer(file)
            return Response(serializer.data)
        
        
        elif folder_id:
            try:
                folder = Folder.objects.get(id=folder_id, owner=request.user)
                files = File.objects.filter(folder=folder, owner=request.user)
            except Folder.DoesNotExist:
                return Response({"error": "Folder not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = FileSerializer(files, many=True)
            return Response(serializer.data)
        
       
        else:
            files = File.objects.filter(owner=request.user, folder=None) 
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data)

    def post(self, request, folder_id=None):
        
        if not folder_id:
            serializer = FileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=request.user, folder=None)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        
        try:
            folder = Folder.objects.get(id=folder_id, owner=request.user)
        except Folder.DoesNotExist:
            return Response({"error": "Folder not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user, folder=folder)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, folder_id, file_id):
        try:
            file = File.objects.get(id=file_id, folder_id=folder_id, owner=request.user)
        except File.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        
        file.name = request.data.get('name', file.name)
        new_file = request.FILES.get('file')
        if new_file:
            file.file = new_file
        file.save()
        return Response({"message": "File updated successfully"}, status=status.HTTP_200_OK)
    


    def delete(self, request, file_id):
        try:
            file_instance = File.objects.get(id=file_id)
            file_instance.delete()
            return Response({"message": "File deleted successfully"}, status=status.HTTP_200_OK)
        except File.DoesNotExist:
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
