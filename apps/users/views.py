from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, Role
from .serializers import (
    UserSerializer, UserCreateSerializer, UserPasswordUpdateSerializer,
    RoleSerializer, LoginSerializer
)
from core.response import APIResponse
from rest_framework.permissions import IsAdminUser
from apps.logs.models import LoginLog
import datetime
import logging

# 获取日志记录器
logger = logging.getLogger('django')


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['username', 'email', 'real_name', 'status', 'role']
    search_fields = ['username', 'email', 'real_name', 'phone']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['post'], serializer_class=UserPasswordUpdateSerializer)
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse(message='密码修改成功')
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        # 设置一个默认密码
        default_password = 'ArtiOps@123'
        user.set_password(default_password)
        user.save()
        return APIResponse(message='密码重置成功', data={'default_password': default_password})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return APIResponse(data=serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], serializer_class=LoginSerializer)
    def login(self, request):
        try:
            # 记录请求数据，用于调试
            logger.info(f"Login attempt with data: {request.data}")
            
            serializer = self.get_serializer(data=request.data)
            
            # 详细记录验证错误
            if not serializer.is_valid():
                logger.error(f"Login validation errors: {serializer.errors}")
                return APIResponse(code=400, message=f"验证错误: {serializer.errors}", status=status.HTTP_400_BAD_REQUEST)
            
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            ip_address = serializer.validated_data.get('ip_address')
            
            logger.info(f"Attempting to authenticate user: {username}")
            
            user = authenticate(username=username, password=password)
            
            if not user:
                logger.warning(f"Authentication failed for user: {username}")
                return APIResponse(code=400, message='用户名或密码错误', status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"User authenticated successfully: {username}")
            
            # 检查用户状态
            if hasattr(user, 'status') and not user.status:
                logger.warning(f"User account is disabled: {username}")
                return APIResponse(code=403, message='账号已被禁用', status=status.HTTP_403_FORBIDDEN)
            
            # 更新最后登录信息
            user.last_login = timezone.now()
            
            # 检查last_login_ip字段是否存在
            if hasattr(user, 'last_login_ip') and ip_address:
                user.last_login_ip = ip_address
                user.save(update_fields=['last_login', 'last_login_ip'])
            else:
                user.save(update_fields=['last_login'])
            
            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"Login successful for user: {username}")
            
            return APIResponse(message='登录成功', data={
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        
        except Exception as e:
            # 记录任何未预期的异常
            logger.exception(f"Unexpected error during login: {str(e)}")
            return APIResponse(code=500, message=f"登录过程中发生错误: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        # JWT无状态，客户端只需删除令牌
        return APIResponse(message='退出成功')


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色管理视图集
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['name', 'key']
    search_fields = ['name', 'key', 'description']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['id']
    
    def get_permissions(self):
        return [IsAdminUser()] 