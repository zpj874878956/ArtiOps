from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, UserLoginLog
from .serializers import (
    UserSerializer, UserCreateSerializer, UserLoginSerializer,
    UserProfileSerializer, ChangePasswordSerializer, UserLoginLogSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    用户视图集
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        elif self.action == 'profile':
            return UserProfileSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return self.serializer_class
    
    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_description="用户注册接口",
        request_body=UserCreateSerializer,
        responses={201: UserSerializer}
    )
    def create(self, request, *args, **kwargs):
        """用户注册"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 返回用户信息和token
        refresh = RefreshToken.for_user(user)
        response_data = UserSerializer(user).data
        response_data['refresh'] = str(refresh)
        response_data['access'] = str(refresh.access_token)
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="用户登录接口",
        request_body=UserLoginSerializer,
        responses={200: openapi.Response(
            description="登录成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )}
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # 记录登录信息
        login(request, user)
        
        # 记录登录日志
        UserLoginLog.objects.create(
            user=user,
            login_ip=self.get_client_ip(request),
            login_type='web',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            is_success=True
        )
        
        # 更新最后登录IP
        user.last_login_ip = self.get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
    @swagger_auto_schema(
        operation_description="用户登出接口",
        responses={200: openapi.Response(description="登出成功")}
    )
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """用户登出"""
        logout(request)
        return Response({"detail": _("成功登出")})
    
    @swagger_auto_schema(
        method='get',
        operation_description="获取当前用户信息",
        responses={200: UserProfileSerializer}
    )
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        methods=['put', 'patch'],
        operation_description="更新当前用户信息",
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    )
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """更新当前用户信息"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="修改密码",
        request_body=ChangePasswordSerializer,
        responses={200: openapi.Response(description="密码修改成功")}
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 修改密码
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({"detail": _("密码修改成功")})
    
    def get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户登录日志视图集
    """
    serializer_class = UserLoginLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # 管理员可以查看所有日志，普通用户只能查看自己的日志
        user = self.request.user
        if user.is_admin or user.is_superuser:
            return UserLoginLog.objects.all()
        return UserLoginLog.objects.filter(user=user)
