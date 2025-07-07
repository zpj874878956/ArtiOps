from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Host, HostGroup, HostTag, SSHCredential

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器（简化版）"""
    class Meta:
        model = User
        fields = ('id', 'username')


class HostGroupSerializer(serializers.ModelSerializer):
    """主机组序列化器"""
    created_by = UserSerializer(read_only=True)
    host_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HostGroup
        fields = ('id', 'name', 'description', 'created_by', 'created_at', 'updated_at', 'host_count')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_host_count(self, obj):
        """获取主机组中的主机数量"""
        return obj.hosts.count()
    
    def create(self, validated_data):
        """创建主机组"""
        # 设置创建人为当前用户
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class HostTagSerializer(serializers.ModelSerializer):
    """主机标签序列化器"""
    created_by = UserSerializer(read_only=True)
    host_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HostTag
        fields = ('id', 'name', 'color', 'created_by', 'created_at', 'host_count')
        read_only_fields = ('created_at',)
    
    def get_host_count(self, obj):
        """获取标签关联的主机数量"""
        return obj.hosts.count()
    
    def create(self, validated_data):
        """创建主机标签"""
        # 设置创建人为当前用户
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class HostSerializer(serializers.ModelSerializer):
    """主机序列化器"""
    created_by = UserSerializer(read_only=True)
    groups = HostGroupSerializer(many=True, read_only=True)
    tags = HostTagSerializer(many=True, read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(
        queryset=HostGroup.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='groups'
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=HostTag.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='tags'
    )
    
    class Meta:
        model = Host
        fields = ('id', 'hostname', 'ip_address', 'port', 'os_type', 'os_version', 'status',
                  'description', 'created_by', 'created_at', 'updated_at', 'groups', 'tags',
                  'group_ids', 'tag_ids')
        read_only_fields = ('created_at', 'updated_at')
    
    def create(self, validated_data):
        """创建主机"""
        # 设置创建人为当前用户
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SSHCredentialSerializer(serializers.ModelSerializer):
    """SSH凭证序列化器"""
    created_by = UserSerializer(read_only=True)
    hosts = HostSerializer(many=True, read_only=True)
    host_ids = serializers.PrimaryKeyRelatedField(
        queryset=Host.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='hosts'
    )
    
    class Meta:
        model = SSHCredential
        fields = ('id', 'name', 'auth_type', 'username', 'password', 'private_key', 'passphrase',
                  'is_default', 'description', 'created_by', 'created_at', 'updated_at', 'hosts', 'host_ids')
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'password': {'write_only': True},
            'private_key': {'write_only': True},
            'passphrase': {'write_only': True},
        }
    
    def create(self, validated_data):
        """创建SSH凭证"""
        # 设置创建人为当前用户
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SSHCredentialCreateSerializer(serializers.ModelSerializer):
    """SSH凭证创建序列化器
    用于创建和更新SSH凭证，包含更严格的验证
    """
    host_ids = serializers.PrimaryKeyRelatedField(
        queryset=Host.objects.all(),
        many=True,
        required=False,
        source='hosts'
    )
    
    class Meta:
        model = SSHCredential
        fields = ('name', 'auth_type', 'username', 'password', 'private_key', 'passphrase',
                  'is_default', 'host_ids', 'description')
        extra_kwargs = {
            'password': {'write_only': True},
            'private_key': {'write_only': True},
            'passphrase': {'write_only': True},
        }
    
    def validate(self, data):
        """验证数据"""
        auth_type = data.get('auth_type')
        password = data.get('password')
        private_key = data.get('private_key')
        
        # 创建时验证认证信息
        if self.instance is None:  # 创建操作
            if auth_type == 'password' and not password:
                raise serializers.ValidationError({'password': '密码认证类型必须提供密码'})
            elif auth_type == 'key' and not private_key:
                raise serializers.ValidationError({'private_key': '密钥认证类型必须提供私钥'})
        # 更新时，如果提供了认证类型但没有提供对应的认证信息，则验证
        elif 'auth_type' in self.initial_data:
            if auth_type == 'password' and 'password' in self.initial_data and not password:
                raise serializers.ValidationError({'password': '密码认证类型必须提供密码'})
            elif auth_type == 'key' and 'private_key' in self.initial_data and not private_key:
                raise serializers.ValidationError({'private_key': '密钥认证类型必须提供私钥'})
        
        return data