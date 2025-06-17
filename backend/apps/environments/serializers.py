from rest_framework import serializers
from .models import Environment


class EnvironmentSerializer(serializers.ModelSerializer):
    """
    环境序列化器
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Environment
        fields = ['id', 'name', 'type', 'description', 'api_endpoint', 'project', 'project_name',
                 'variables', 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data) 