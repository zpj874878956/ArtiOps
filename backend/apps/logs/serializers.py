from rest_framework import serializers
from .models import LoginLog, OperationLog


class LoginLogSerializer(serializers.ModelSerializer):
    """
    登录日志序列化器
    """
    user_name = serializers.CharField(source='user.username', read_only=True, default='')
    
    class Meta:
        model = LoginLog
        fields = ['id', 'username', 'user_name', 'ip_address', 'login_time', 
                 'status', 'message', 'user_agent', 'user']
        read_only_fields = ['id', 'login_time']


class OperationLogSerializer(serializers.ModelSerializer):
    """
    操作日志序列化器
    """
    user_name = serializers.CharField(source='user.username', read_only=True, default='')
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = ['id', 'username', 'user_name', 'ip_address', 'operation_time',
                 'action', 'action_display', 'resource_type', 'resource_type_display',
                 'resource_id', 'resource_name', 'content', 'status', 'user']
        read_only_fields = ['id', 'operation_time'] 