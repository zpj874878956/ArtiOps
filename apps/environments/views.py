from rest_framework import viewsets
from .models import Environment
from .serializers import EnvironmentSerializer
from core.permissions import RoleBasedPermission
from django.db.models import Q


class EnvironmentViewSet(viewsets.ModelViewSet):
    """
    环境管理视图
    """
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
    filterset_fields = ['name', 'type', 'project']
    search_fields = ['name', 'description', 'api_endpoint']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    ordering = ['id']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [RoleBasedPermission('environment_manage')]
        return [RoleBasedPermission('environment_view')]
    
    def get_queryset(self):
        user = self.request.user
        # 超级管理员可以看到所有环境
        if user.is_superuser:
            return Environment.objects.all()
            
        # 普通用户只能看到自己有权限的项目下的环境
        return Environment.objects.filter(
            Q(project__owner=user) | 
            Q(project__created_by=user) | 
            Q(project__members__user=user)
        ).distinct() 