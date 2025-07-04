from rest_framework import serializers
from .models import CommandTemplate, CommandExecution, ExecutionLog, DangerousCommand
from django.utils.translation import gettext_lazy as _


class CommandTemplateSerializer(serializers.ModelSerializer):
    """
    命令模板序列化器
    用于命令模板的创建、更新和展示
    """
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = CommandTemplate
        fields = ['id', 'name', 'template_type', 'content', 'description', 
                  'is_public', 'created_at', 'updated_at', 'created_by', 'created_by_username']
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        # 设置创建人为当前用户
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CommandExecutionSerializer(serializers.ModelSerializer):
    """
    命令执行记录序列化器
    用于创建和展示命令执行记录
    """
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    template_name = serializers.ReadOnlyField(source='template.name')
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = CommandExecution
        fields = ['id', 'name', 'execution_type', 'command_content', 'template', 'template_name',
                  'target_hosts', 'parameters', 'result', 'status', 'start_time', 'end_time',
                  'created_at', 'created_by', 'created_by_username', 'duration']
        read_only_fields = ['id', 'created_at', 'created_by', 'start_time', 'end_time', 'status', 'result']
    
    def get_duration(self, obj):
        """计算执行持续时间（秒）"""
        if obj.start_time and obj.end_time:
            return (obj.end_time - obj.start_time).total_seconds()
        return None
    
    def create(self, validated_data):
        # 设置创建人为当前用户
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ExecutionLogSerializer(serializers.ModelSerializer):
    """
    执行日志序列化器
    用于展示命令执行日志
    """
    class Meta:
        model = ExecutionLog
        fields = ['id', 'execution', 'host', 'log_level', 'message', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class DangerousCommandSerializer(serializers.ModelSerializer):
    """
    危险命令序列化器
    用于危险命令的创建、更新和展示
    """
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = DangerousCommand
        fields = ['id', 'pattern', 'command_type', 'description', 'action', 
                  'created_at', 'created_by', 'created_by_username']
        read_only_fields = ['created_at', 'created_by']
    
    def create(self, validated_data):
        # 设置创建人为当前用户
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CommandExecutionCreateSerializer(serializers.ModelSerializer):
    """
    命令执行创建序列化器
    用于创建新的命令执行任务，包含更严格的验证
    """
    class Meta:
        model = CommandExecution
        fields = ['name', 'execution_type', 'command_content', 'template', 'target_hosts', 'parameters']
    
    def validate(self, data):
        # 验证命令内容不能为空
        if not data.get('command_content') and not data.get('template'):
            raise serializers.ValidationError(_('命令内容和模板不能同时为空'))
        
        # 验证目标主机不能为空
        if not data.get('target_hosts'):
            raise serializers.ValidationError(_('目标主机不能为空'))
        
        # 如果使用模板，自动填充命令内容
        if data.get('template') and not data.get('command_content'):
            data['command_content'] = data['template'].content
            data['execution_type'] = data['template'].template_type
        
        return data