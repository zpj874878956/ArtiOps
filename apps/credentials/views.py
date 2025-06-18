from rest_framework import viewsets
from .models import Credential, CredentialUsageLog
from .serializers import CredentialSerializer, CredentialCreateSerializer, CredentialUpdateSerializer, CredentialUsageLogSerializer
from core.permissions import RoleBasedPermission
from core.response import success_response, error_response
from rest_framework.decorators import action


class CredentialViewSet(viewsets.ModelViewSet):
    """
    凭据管理视图集
    """
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer
    filterset_fields = ['name', 'credential_type', 'created_by']
    search_fields = ['name', 'description', 'username']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [RoleBasedPermission('credential_manage')]
        return [RoleBasedPermission('credential_view')]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CredentialCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CredentialUpdateSerializer
        return CredentialSerializer
    
    def get_queryset(self):
        user = self.request.user
        # 超级管理员可以看到所有凭据
        if user.is_superuser:
            return Credential.objects.all()
            
        # 普通用户只能看到自己创建的凭据
        return Credential.objects.filter(created_by=user)
    
    @action(detail=True, methods=['post'])
    def log_usage(self, request, pk=None):
        """
        记录凭据使用
        """
        credential = self.get_object()
        action = request.data.get('action', '')
        task_info = request.data.get('task_info', {})
        ip_address = request.META.get('REMOTE_ADDR', '')
        
        # 创建使用日志
        usage_log = CredentialUsageLog.objects.create(
            credential=credential,
            user=request.user,
            ip_address=ip_address,
            action=action,
            task_info=task_info
        )
        
        return success_response({
            'id': usage_log.id,
            'created_at': usage_log.used_at
        }, message='凭据使用已记录')


class CredentialUsageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    凭据使用日志视图集（只读）
    """
    queryset = CredentialUsageLog.objects.all()
    serializer_class = CredentialUsageLogSerializer
    filterset_fields = ['credential', 'user', 'action']
    ordering_fields = ['id', 'used_at']
    ordering = ['-used_at']
    
    def get_permissions(self):
        return [RoleBasedPermission('credential_view')]
    
    def get_queryset(self):
        user = self.request.user
        # 超级管理员可以看到所有日志
        if user.is_superuser:
            return CredentialUsageLog.objects.all()
            
        # 普通用户只能看到自己创建的凭据的使用日志
        return CredentialUsageLog.objects.filter(credential__created_by=user) 