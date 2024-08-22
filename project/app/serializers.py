from rest_framework import serializers
from .models import Task 
# this converts model instances to Python Data, allows rendering as JSON
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'creator', 'executor', 'name', 'cost', 'is_done', 'deadline']




