from rest_framework import viewsets
from .models import LoginLog, OperationLog
from .serializers import LoginLogSerializer, OperationLogSerializer
from core.permissions import RoleBasedPermission
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class LoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    登录日志视图集（只读）
    """
    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'username', 'ip_address']
    search_fields = ['username', 'ip_address', 'user_agent']
    ordering_fields = ['id', 'login_time']
    ordering = ['-login_time']
    
    def get_permissions(self):
        return [RoleBasedPermission('log_view')]


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    操作日志视图集（只读）
    """
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'resource_type', 'username', 'status']
    search_fields = ['username', 'ip_address', 'resource_name', 'content']
    ordering_fields = ['id', 'operation_time']
    ordering = ['-operation_time']
    
    def get_permissions(self):
        return [RoleBasedPermission('log_view')] 