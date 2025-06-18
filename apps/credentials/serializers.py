from rest_framework import serializers
from .models import Credential, CredentialUsageLog
from core.encryption import AESCipher


class CredentialSerializer(serializers.ModelSerializer):
    """
    凭据序列化器（用于列表和详情）
    """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    credential_type_display = serializers.CharField(source='get_credential_type_display', read_only=True)
    
    class Meta:
        model = Credential
        fields = ['id', 'name', 'credential_type', 'credential_type_display', 'description', 
                 'username', 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_at', 'updated_at']


class CredentialCreateSerializer(serializers.ModelSerializer):
    """
    凭据创建序列化器
    """
    class Meta:
        model = Credential
        fields = ['id', 'name', 'credential_type', 'description', 'username', 'password',
                 'private_key', 'key_passphrase', 'token', 'extra_data']
        read_only_fields = ['id']
        
    def create(self, validated_data):
        # 设置创建者
        validated_data['created_by'] = self.context['request'].user
        
        # 加密敏感字段
        self._encrypt_sensitive_fields(validated_data)
        
        return super().create(validated_data)
    
    def _encrypt_sensitive_fields(self, data):
        """加密敏感字段"""
        cipher = AESCipher()
        sensitive_fields = ['password', 'private_key', 'key_passphrase', 'token']
        
        for field in sensitive_fields:
            if field in data and data[field]:
                data[field] = cipher.encrypt(data[field])


class CredentialUpdateSerializer(serializers.ModelSerializer):
    """
    凭据更新序列化器
    """
    class Meta:
        model = Credential
        fields = ['name', 'description', 'username', 'password',
                'private_key', 'key_passphrase', 'token', 'extra_data']
    
    def update(self, instance, validated_data):
        # 加密敏感字段
        self._encrypt_sensitive_fields(validated_data)
        
        return super().update(instance, validated_data)
    
    def _encrypt_sensitive_fields(self, data):
        """加密敏感字段"""
        cipher = AESCipher()
        sensitive_fields = ['password', 'private_key', 'key_passphrase', 'token']
        
        for field in sensitive_fields:
            if field in data and data[field]:
                data[field] = cipher.encrypt(data[field])


class CredentialUsageLogSerializer(serializers.ModelSerializer):
    """
    凭据使用日志序列化器
    """
    credential_name = serializers.CharField(source='credential.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CredentialUsageLog
        fields = ['id', 'credential', 'credential_name', 'user', 'user_name',
                 'ip_address', 'used_at', 'action', 'task_info']
        read_only_fields = ['id', 'credential', 'user', 'used_at'] 