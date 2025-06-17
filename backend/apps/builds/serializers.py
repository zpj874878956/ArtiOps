from rest_framework import serializers
from .models import BuildTask, BuildHistory
from apps.projects.serializers import ProjectSerializer
from apps.credentials.serializers import CredentialSerializer
from apps.users.serializers import UserSerializer


class BuildTaskSerializer(serializers.ModelSerializer):
    """
    构建任务序列化器
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BuildTask
        fields = ['id', 'name', 'description', 'project', 'project_name', 
                 'command', 'parameters', 'environment_variables', 'status', 'status_display',
                 'is_scheduled', 'schedule', 'timeout', 'created_by', 'created_by_name', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'status_display', 'created_by', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BuildTaskDetailSerializer(BuildTaskSerializer):
    """
    构建任务详情序列化器
    """
    project_detail = ProjectSerializer(source='project', read_only=True)
    credential_detail = CredentialSerializer(source='credential', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    histories = serializers.SerializerMethodField()
    
    class Meta(BuildTaskSerializer.Meta):
        fields = BuildTaskSerializer.Meta.fields + ['project_detail', 'credential_detail', 
                                                  'created_by_detail', 'histories']
    
    def get_histories(self, obj):
        # 获取最近的5条构建历史
        histories = obj.build_histories.all()[:5]
        return BuildHistorySerializer(histories, many=True).data


class BuildHistorySerializer(serializers.ModelSerializer):
    """
    构建历史序列化器
    """
    task_name = serializers.CharField(source='task.name', read_only=True)
    executed_by_name = serializers.CharField(source='executed_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BuildHistory
        fields = ['id', 'task', 'task_name', 'build_number', 'status', 'status_display', 
                 'execution_path', 'log_file', 'started_at', 'finished_at', 
                 'duration', 'executed_by', 'executed_by_name']
        read_only_fields = ['id', 'task', 'build_number', 'execution_path', 'log_file', 
                          'started_at', 'finished_at', 'duration', 'executed_by']


class BuildHistoryDetailSerializer(BuildHistorySerializer):
    """
    构建历史详情序列化器
    """
    task_detail = BuildTaskSerializer(source='task', read_only=True)
    executed_by_detail = UserSerializer(source='executed_by', read_only=True)
    log_content = serializers.SerializerMethodField()
    
    class Meta(BuildHistorySerializer.Meta):
        fields = BuildHistorySerializer.Meta.fields + ['task_detail', 'executed_by_detail', 
                                                     'log_content']
    
    def get_log_content(self, obj):
        """
        获取日志内容
        """
        if not obj.log_file:
            return ""
            
        try:
            with open(obj.log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return "无法读取日志文件" 