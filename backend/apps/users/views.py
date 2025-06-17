from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import User, Role
from .serializers import (
    UserSerializer, UserCreateSerializer, UserPasswordUpdateSerializer,
    RoleSerializer, LoginSerializer
)
from core.response import success_response, error_response
from core.permissions import RoleBasedPermission
from apps.logs.models import LoginLog
import datetime


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ['username', 'real_name', 'status', 'role']
    search_fields = ['username', 'real_name', 'email', 'phone']
    ordering_fields = ['id', 'username', 'date_joined', 'last_login']
    ordering = ['-id']
    
    def get_permissions(self):
        if self.action == 'login':
            return [permissions.AllowAny()]
        elif self.action in ['create', 'list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [RoleBasedPermission('user_manage')]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'update_password':
            return UserPasswordUpdateSerializer
        elif self.action == 'login':
            return LoginSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        用户登录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        ip_address = serializer.validated_data.get('ip_address')
        
        # 查找用户
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 记录登录失败日志
            LoginLog.objects.create(
                username=username,
                ip_address=ip_address or request.META.get('REMOTE_ADDR', ''),
                status=False,
                message='用户不存在'
            )
            return error_response(message='用户名或密码错误', code=400)
        
        # 验证密码
        if not user.check_password(password):
            # 记录登录失败日志
            LoginLog.objects.create(
                username=username,
                ip_address=ip_address or request.META.get('REMOTE_ADDR', ''),
                status=False,
                message='密码错误'
            )
            return error_response(message='用户名或密码错误', code=400)
        
        # 检查用户状态
        if not user.status:
            return error_response(message='账户已被禁用', code=403)
            
        # 更新登录信息
        user.last_login = timezone.now()
        user.last_login_ip = ip_address or request.META.get('REMOTE_ADDR', '')
        user.save(update_fields=['last_login', 'last_login_ip'])
        
        # 记录登录成功日志
        LoginLog.objects.create(
            username=username,
            ip_address=ip_address or request.META.get('REMOTE_ADDR', ''),
            status=True,
            user=user
        )
        
        # 生成Token
        refresh = RefreshToken.for_user(user)
        
        return success_response({
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'role': user.role_id,
            'role_name': user.role.name if user.role else None,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, message='登录成功')
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        用户登出
        """
        # 这里不做token失效处理，前端自行清除token即可
        return success_response(message='登出成功')
    
    @action(detail=True, methods=['post'])
    def update_password(self, request, pk=None):
        """
        修改密码
        """
        user = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message='密码修改成功')
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        重置密码
        """
        user = self.get_object()
        # 设置为默认密码，实际应用中可能需要生成随机密码并发送邮件
        default_password = '123456'
        user.set_password(default_password)
        user.save()
        return success_response(message='密码重置成功')
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        切换用户状态
        """
        user = self.get_object()
        user.status = not user.status
        user.save(update_fields=['status'])
        return success_response(message=f'用户已{"启用" if user.status else "禁用"}')


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色管理视图
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filterset_fields = ['name', 'key']
    search_fields = ['name', 'key', 'description']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['id']
    
    def get_permissions(self):
        return [RoleBasedPermission('role_manage')] 