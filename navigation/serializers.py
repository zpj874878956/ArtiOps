from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import SystemCategory, ExternalSystem, SystemPermission, UserFavorite, AccessLog
from users.serializers import UserSerializer


class SystemCategorySerializer(serializers.ModelSerializer):
    """
    系统分类序列化器
    """
    class Meta:
        model = SystemCategory
        fields = ['id', 'name', 'description', 'icon', 'order', 'created_at', 'updated_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemCategoryDetailSerializer(SystemCategorySerializer):
    """
    系统分类详情序列化器，包含创建者信息
    """
    created_by = UserSerializer(read_only=True)


class ExternalSystemSerializer(serializers.ModelSerializer):
    """
    外部系统序列化器
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ExternalSystem
        fields = [
            'id', 'name', 'system_type', 'category', 'category_name', 'base_url', 
            'icon', 'description', 'status', 'is_active', 'auth_type', 'auth_config',
            'order', 'access_count', 'score', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'access_count', 'score', 'created_at', 'updated_at']
        extra_kwargs = {
            'auth_config': {'write_only': True}  # 认证配置信息不应在API响应中返回
        }


class ExternalSystemDetailSerializer(ExternalSystemSerializer):
    """
    外部系统详情序列化器，包含创建者和分类信息
    """
    created_by = UserSerializer(read_only=True)
    category = SystemCategorySerializer(read_only=True)


class SystemPermissionSerializer(serializers.ModelSerializer):
    """
    系统权限序列化器
    """
    system_name = serializers.CharField(source='system.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = SystemPermission
        fields = ['id', 'system', 'system_name', 'user', 'user_username', 'group', 'group_name', 'can_access', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, attrs):
        # 验证用户和用户组至少有一个
        if not attrs.get('user') and not attrs.get('group'):
            raise serializers.ValidationError(_('用户和用户组必须至少指定一个'))
        return attrs


class UserFavoriteSerializer(serializers.ModelSerializer):
    """
    用户收藏序列化器
    """
    system_detail = ExternalSystemSerializer(source='system', read_only=True)
    
    class Meta:
        model = UserFavorite
        fields = ['id', 'user', 'system', 'system_detail', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, attrs):
        # 验证用户是否已收藏该系统
        user = attrs.get('user')
        system = attrs.get('system')
        if UserFavorite.objects.filter(user=user, system=system).exists():
            raise serializers.ValidationError(_('已收藏该系统'))
        return attrs


class AccessLogSerializer(serializers.ModelSerializer):
    """
    访问日志序列化器
    """
    username = serializers.CharField(source='user.username', read_only=True)
    system_name = serializers.CharField(source='system.name', read_only=True)
    
    class Meta:
        model = AccessLog
        fields = ['id', 'user', 'username', 'system', 'system_name', 'access_time', 'access_ip', 'user_agent']
        read_only_fields = fields