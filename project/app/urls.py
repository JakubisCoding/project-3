from django.urls import path
from .views import *

urlpatterns = [
    path('user/create/', UserCreateView.as_view(), name='user_create'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('task/create/', TaskCreateView.as_view(), name='task_create'), # type: ignore
    # path('tasks-created-by-user/', TasksCreatedByUser.as_view(), name='user_tasks'), # type: ignore
    # path('user-tasks-stats/', UserTasksStatsAPIView.as_view(), name='user-tasks-stats'), # type: ignore
    # path('unassigned-tasks/', UnassignedTasksAPIView.as_view(), name='unassigned-tasks'), # type: ignore
    # path('task/executor/', TaskWithExecutorAPIView.as_view(), name='task_executor'), # type: ignore
    # path('user-tasks/', UserTasksAPIView.as_view(), name='my-tasks'), # type: ignore
    # path('become-executor/<int:task_id>/', BecomeExecutorAPIView.as_view(), name='become-executor'), # type: ignore
    # path('mark-task-done/<int:task_id>/', MarkTaskDoneAPIView.as_view(), name='mark-task-done'), # type: ignore
    path('clear_db/', ClearDatabaseView.as_view(), name='clear_db'),
]