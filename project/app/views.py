from django.shortcuts import render
from rest_framework.views import *
from django.contrib.auth.models import User
from rest_framework import status 
from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token

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
    def post(self, request):
        # Custom authentication class handles invalid tokens
        if request.user and request.user.is_authenticated:
            try:
                # Attempt to retrieve and delete the token
                token = Token.objects.get(user=request.user)
                token.delete()

                # Log the user out
                logout(request)

                return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
            except Token.DoesNotExist:
                #message for invalid tokens
                return Response({'detail': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
               
            


           
    
    
class ClearDatabaseView(APIView):
    def get(self, request):
        #Task.objects.all().delete()
        User.objects.all().delete()
        return Response({'message': 'All data cleared successfully'}, status=200)
    












# 1. Implement the `post` method to handle POST requests for creating a new user.
# 2. Check for the presence of: `username`, `password`, and `email`. If any of these values are missing in the request body,
#  return an error message `{'error': 'Username, password, and email are required'}` with the status code `400 BAD REQUEST`.
# 3. Check if a user with the specified `username` already exists. If a user with this username already exists,
# return an error message `{'error': 'Username already exists'}` with the status code `400 BAD REQUEST`.
# 4. If all data is valid, create a new user. Upon successful creation of the user,
# return a user data (id, username, email) in JSON format with the status code `201 CREATED`.

# Hint: To work with the `User` model and send HTTP responses,
#  use the appropriate functions from Django REST Framework: `User.objects.create_user`, `Response`