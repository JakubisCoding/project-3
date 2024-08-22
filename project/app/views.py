
from django.shortcuts import render, redirect
from rest_framework.views import *
from django.contrib.auth.models import User
from rest_framework import status 
from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TaskSerializer
from .models import *


from django.utils import timezone
from django.db.models import Sum, Count
from rest_framework import generics



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
           
               
            









# Create your views here.

class TaskCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        creator_id = request.user.pk
        executor_id = data.get('executor')

        #creator is not the same as the executor
        if executor_id and creator_id == int(executor_id):
            return Response({'error': 'The creator of a task cannot be its executor'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the executor if provided
        if executor_id:
            if not User.objects.filter(id=executor_id).exists():
                data['executor'] = None

        # Include the creator in the data
        data['creator'] = creator_id
        print("[+] data: ", data)
        # Create a serializer instance with the updated data
        serializer = TaskSerializer(data=data)

        # Validate and save the data
        if serializer.is_valid():
            task = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TasksCreatedByUser(APIView):
    authentication_classes = [TokenAuthentication]

    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view

    def get(self, request):
        user = request.user
        # Filter tasks where the creator is the current user
        tasks = Task.objects.filter(creator=user)
        serializer = TaskSerializer(tasks, many=True)

        # Return the serialized data as a JSON response
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class TaskWithExecutorAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        print("Received GET request from user:", request.user)
        tasks = Task.objects.all()
        print("Tasks fetched:", tasks)
        serialized_tasks = []
        for task in tasks:
            data = {
                'executor': task.executor.username if task.executor else 'undefined',
                'name': task.name,
                'cost': f'{task.cost:.2f}',
                'deadline': task.deadline,
            }
            serialized_tasks.append(data)
        print("Serialized tasks:", serialized_tasks)
        return Response(serialized_tasks, status=status.HTTP_200_OK)

class ClearDatabaseView(APIView):
    def get(self, request):
        Task.objects.all().delete()
        User.objects.all().delete()
        return Response({'message': 'All data cleared successfully'}, status=200)



class UserTasksStatsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        completed_tasks = Task.objects.filter(creator=user, is_done=True).count()
        pending_tasks = Task.objects.filter(creator=user, is_done=False).count()
        overdue_tasks = Task.objects.filter(creator=user, is_done=False, deadline__lt=timezone.now()).count()
        assigned_tasks = Task.objects.filter(executor=user).count()
        total_earned = Task.objects.filter(executor=user, is_done=True).aggregate(Sum('cost'))['cost__sum']
        total_spent = Task.objects.filter(creator=user).aggregate(Sum('cost'))['cost__sum']

        stats_data = {
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'assigned_tasks': assigned_tasks,
            'total_earned': total_earned if total_earned else 0,
            'total_spent': total_spent if total_spent else 0,
        }

        return Response(stats_data, status=status.HTTP_200_OK)
    
class UnassignedTasksAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unassigned_tasks = Task.objects.filter(executor__isnull=True).order_by('cost')

        serializer = TaskSerializer(unassigned_tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserTasksAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(executor=user.pk)
        return queryset
    

class BecomeExecutorAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        user = request.user

        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        if task.creator == user:
            return Response({'error': 'You cannot assign yourself as executor of your own task'},
                            status=status.HTTP_400_BAD_REQUEST)

        if task.executor:
            return Response({'error': 'This task already has an executor'},
                            status=status.HTTP_400_BAD_REQUEST)

        task.executor = user
        task.save()

        return Response({'message': 'You have been assigned as the executor of the task'},
                        status=status.HTTP_200_OK)
    

class MarkTaskDoneAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        if task.executor != request.user:
            return Response({'error': 'You are not authorized to mark this task as done'},
                            status=status.HTTP_403_FORBIDDEN)

        task.is_done = True
        task.save()

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)