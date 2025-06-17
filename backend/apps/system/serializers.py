from rest_framework import serializers
from .models import SystemConfig
from core.encryption import AESCipher


class SystemConfigSerializer(serializers.ModelSerializer):
    """
    系统配置序列化器
    """
    class Meta:
        model = SystemConfig
        fields = ['id', 'key', 'value', 'description', 'is_encrypted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def to_representation(self, instance):
        # 加密字段的解密处理
        ret = super().to_representation(instance)
        if instance.is_encrypted:
            cipher = AESCipher()
            try:
                ret['value'] = cipher.decrypt(ret['value'])
            except Exception:
                ret['value'] = "**加密数据**"
        return ret
    
    def create(self, validated_data):
        # 加密字段的加密处理
        if validated_data.get('is_encrypted') and validated_data.get('value'):
            cipher = AESCipher()
            validated_data['value'] = cipher.encrypt(validated_data['value'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # 加密字段的加密处理
        if validated_data.get('is_encrypted', instance.is_encrypted) and 'value' in validated_data:
            cipher = AESCipher()
            validated_data['value'] = cipher.encrypt(validated_data['value'])
        return super().update(instance, validated_data) 