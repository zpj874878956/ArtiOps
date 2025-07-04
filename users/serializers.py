from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User, UserLoginLog


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 
                  'phone', 'department', 'position', 'avatar', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    用户创建序列化器
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 
                  'user_type', 'phone', 'department', 'position']
    
    def validate(self, attrs):
        # 验证两次密码是否一致
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": _("两次密码不一致")})
        return attrs
    
    def create(self, validated_data):
        # 移除password_confirm字段
        validated_data.pop('password_confirm', None)
        # 创建用户
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # 验证用户名和密码
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                msg = _('无法使用提供的凭据登录')
                raise serializers.ValidationError(msg, code='authorization')
            if not user.is_active:
                raise serializers.ValidationError(_('用户账号已被禁用'), code='authorization')
        else:
            msg = _('必须包含用户名和密码')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户个人资料序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 
                  'phone', 'department', 'position', 'avatar', 'is_active', 'date_joined']
        read_only_fields = ['id', 'username', 'user_type', 'date_joined']


class ChangePasswordSerializer(serializers.Serializer):
    """
    修改密码序列化器
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        # 验证两次新密码是否一致
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({"new_password": _("两次新密码不一致")})
        return attrs
    
    def validate_old_password(self, value):
        # 验证旧密码是否正确
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('旧密码不正确'))
        return value


class UserLoginLogSerializer(serializers.ModelSerializer):
    """
    用户登录日志序列化器
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserLoginLog
        fields = ['id', 'username', 'login_time', 'login_ip', 'login_type', 'user_agent', 'is_success', 'fail_reason']
        read_only_fields = fields