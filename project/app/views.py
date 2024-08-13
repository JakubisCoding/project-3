from django.shortcuts import render, redirect
from rest_framework.views import *
from django.contrib.auth.models import User
from rest_framework import status 
from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.contrib.auth import logout as django_logout
from rest_framework.authentication import TokenAuthentication


#from .models import Task 



#This view allows for the creation of a user.
class UserCreateView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        # check if all credentials are provided
        if not username or not password or not email:
            return Response({'error': 'Username, password, and email are required'}, status=status.HTTP_400_BAD_REQUEST)
        # check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        # create user
        user = User.objects.create_user(username=username, password=password, email=email)

        return Response(
            {'id': user.id, 'username': user.username, 'email': user.email},
            status=status.HTTP_201_CREATED
        )
    
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        # attempting authentication
        user = authenticate(username=username, password=password)
        
        if user:
            # Create or retrieve the user token
            token, created = Token.objects.get_or_create(user=user)
            
            #token in the response
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            # Return error message 
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED  )   

        
    
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if request.user and request.user.is_authenticated:
                # Attempt to retrieve and delete the token
                
                token , create = Token.objects.get_or_create(user=request.user)
                token.delete()

                # Log the user out
                logout(request)

                return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        elif auth_header is None:
             return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)
           
               
            


           
    
    
class ClearDatabaseView(APIView):
    def get(self, request):
        #Task.objects.all().delete()
        User.objects.all().delete()
        return Response({'message': 'All data cleared successfully'}, status=200)
    











