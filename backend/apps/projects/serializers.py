from rest_framework import serializers
from .models import Project, ProjectMember
from apps.users.serializers import UserSerializer


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员序列化器
    """
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'user_info', 'role', 'created_at', 'project']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'project': {'write_only': True}
        }


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目序列化器
    """
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    owner_real_name = serializers.CharField(source='owner.real_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'key', 'description', 'owner', 'owner_name', 
                 'owner_real_name', 'created_by', 'created_by_name', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
        
    def create(self, validated_data):
        # 设置创建人为当前用户
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectDetailSerializer(ProjectSerializer):
    """
    项目详情序列化器，包含成员信息
    """
    members = ProjectMemberSerializer(many=True, read_only=True)
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['members'] 