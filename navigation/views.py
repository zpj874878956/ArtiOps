from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import SystemCategory, ExternalSystem, SystemPermission, UserFavorite, AccessLog
from .serializers import (
    SystemCategorySerializer, SystemCategoryDetailSerializer,
    ExternalSystemSerializer, ExternalSystemDetailSerializer,
    SystemPermissionSerializer, UserFavoriteSerializer, AccessLogSerializer
)


class SystemCategoryViewSet(viewsets.ModelViewSet):
    """
    系统分类视图集
    提供系统分类的CRUD操作
    """
    queryset = SystemCategory.objects.all()
    serializer_class = SystemCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SystemCategoryDetailSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @swagger_auto_schema(
        operation_description="获取系统分类列表",
        responses={200: SystemCategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="创建系统分类",
        request_body=SystemCategorySerializer,
        responses={201: SystemCategorySerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="获取系统分类详情",
        responses={200: SystemCategoryDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="更新系统分类",
        request_body=SystemCategorySerializer,
        responses={200: SystemCategorySerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="部分更新系统分类",
        request_body=SystemCategorySerializer,
        responses={200: SystemCategorySerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="删除系统分类",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ExternalSystemViewSet(viewsets.ModelViewSet):
    """
    外部系统视图集
    提供外部系统的CRUD操作和额外的操作
    """
    serializer_class = ExternalSystemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['system_type', 'category', 'status', 'is_active']
    search_fields = ['name', 'description', 'base_url']
    ordering_fields = ['score', 'order', 'name', 'access_count', 'created_at']
    
    def get_queryset(self):
        """
        根据用户权限过滤可见系统
        """
        user = self.request.user
        if user.is_superuser or user.is_admin:
            return ExternalSystem.objects.all()
            
        # 获取用户有权限访问的系统
        user_systems = ExternalSystem.objects.filter(
            permissions__user=user,
            permissions__can_access=True
        )
        
        # 获取用户所在组有权限访问的系统
        group_systems = ExternalSystem.objects.filter(
            permissions__group__in=user.groups.all(),
            permissions__can_access=True
        )
        
        # 合并结果并去重
        return (user_systems | group_systems).distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExternalSystemDetailSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @swagger_auto_schema(
        operation_description="获取外部系统列表",
        responses={200: ExternalSystemSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="创建外部系统",
        request_body=ExternalSystemSerializer,
        responses={201: ExternalSystemSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="获取外部系统详情",
        responses={200: ExternalSystemDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="更新外部系统",
        request_body=ExternalSystemSerializer,
        responses={200: ExternalSystemSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="部分更新外部系统",
        request_body=ExternalSystemSerializer,
        responses={200: ExternalSystemSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="删除外部系统",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        method='post',
        operation_description="记录系统访问",
        responses={200: openapi.Response(description="访问已记录")}
    )
    @action(detail=True, methods=['post'])
    def record_access(self, request, pk=None):
        """
        记录系统访问
        """
        system = self.get_object()
        
        # 更新系统访问计数
        system.access_count += 1
        system.calculate_score()
        system.save(update_fields=['access_count', 'score'])
        
        # 记录访问日志
        AccessLog.objects.create(
            user=request.user,
            system=system,
            access_ip=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'status': 'access recorded'})
    
    def get_client_ip(self, request):
        """
        获取客户端IP
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SystemPermissionViewSet(viewsets.ModelViewSet):
    """
    系统权限视图集
    提供系统权限的CRUD操作
    """
    queryset = SystemPermission.objects.all()
    serializer_class = SystemPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['system', 'user', 'group', 'can_access']
    
    def get_queryset(self):
        # 管理员可以查看所有权限，普通用户只能查看自己的权限
        user = self.request.user
        if user.is_superuser or user.is_admin:
            return SystemPermission.objects.all()
        return SystemPermission.objects.filter(user=user)
    
    @swagger_auto_schema(
        operation_description="获取系统权限列表",
        responses={200: SystemPermissionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="创建系统权限",
        request_body=SystemPermissionSerializer,
        responses={201: SystemPermissionSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="获取系统权限详情",
        responses={200: SystemPermissionSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="更新系统权限",
        request_body=SystemPermissionSerializer,
        responses={200: SystemPermissionSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="部分更新系统权限",
        request_body=SystemPermissionSerializer,
        responses={200: SystemPermissionSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="删除系统权限",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UserFavoriteViewSet(viewsets.ModelViewSet):
    """
    用户收藏视图集
    提供用户收藏的CRUD操作
    """
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'system']
    
    def get_queryset(self):
        # 用户只能查看自己的收藏，管理员可以查看所有收藏
        user = self.request.user
        if user.is_superuser or user.is_admin:
            return UserFavorite.objects.all()
        return UserFavorite.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="获取用户收藏列表",
        responses={200: UserFavoriteSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="创建用户收藏",
        request_body=UserFavoriteSerializer,
        responses={201: UserFavoriteSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="获取用户收藏详情",
        responses={200: UserFavoriteSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="删除用户收藏",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        method='get',
        operation_description="获取当前用户的收藏列表",
        responses={200: UserFavoriteSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def my_favorites(self, request):
        """
        获取当前用户的收藏列表
        """
        queryset = UserFavorite.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    访问日志视图集
    提供访问日志的只读操作
    """
    serializer_class = AccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'system']
    ordering_fields = ['access_time']
    ordering = ['-access_time']
    
    def get_queryset(self):
        # 管理员可以查看所有日志，普通用户只能查看自己的日志
        user = self.request.user
        if user.is_superuser or user.is_admin:
            return AccessLog.objects.all()
        return AccessLog.objects.filter(user=user)
    
    @swagger_auto_schema(
        operation_description="获取访问日志列表",
        responses={200: AccessLogSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="获取访问日志详情",
        responses={200: AccessLogSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        method='get',
        operation_description="获取当前用户的最近访问记录",
        responses={200: AccessLogSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        获取当前用户的最近访问记录
        """
        queryset = AccessLog.objects.filter(user=request.user).order_by('-access_time')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
