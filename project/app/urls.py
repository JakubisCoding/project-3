from django.urls import path
from .views import *

urlpatterns = [
    path('user/create/', UserCreateView.as_view(), name='user_create'),
    path('app/login/', LoginView.as_view(), name='login'),
    path('app/logout/', LogoutView.as_view(), name='logout'),
    path('task/create/', TaskCreateView.as_view(), name='task_create'),
    path('tasks-created-by-user/', TasksCreatedByUser.as_view(), name='user_tasks'),
    #path('app/user-tasks-stats/', UserTasksStatsAPIView.as_view(), name='user-tasks-stats'),
    #path('app/unassigned-tasks/', UnassignedTasksAPIView.as_view(), name='unassigned-tasks'),
    path('task/executor/', TaskWithExecutorAPIView.as_view(), name='task_executor'),
    #path('app/user-tasks/', UserTasksAPIView.as_view(), name='my-tasks'),
    #path('app/become-executor/<int:task_id>/', BecomeExecutorAPIView.as_view(), name='become-executor'),
    #path('app/mark-task-done/<int:task_id>/', MarkTaskDoneAPIView.as_view(), name='mark-task-done'),
    path('clear_db/', ClearDatabaseView.as_view(), name='clear_db'),
]