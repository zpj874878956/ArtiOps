from rest_framework import viewsets
from .models import SystemConfig
from .serializers import SystemConfigSerializer
from core.permissions import RoleBasedPermission
from core.response import success_response, error_response
from rest_framework.decorators import action
from django.conf import settings
import os
import platform
import json


class SystemConfigViewSet(viewsets.ModelViewSet):
    """
    系统配置视图
    """
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    filterset_fields = ['key', 'is_encrypted']
    search_fields = ['key', 'description']
    ordering_fields = ['key', 'created_at', 'updated_at']
    ordering = ['key']
    
    def get_permissions(self):
        return [RoleBasedPermission('system_manage')]
    
    @action(detail=False, methods=['get'])
    def system_info(self, request):
        """
        获取系统信息
        """
        system_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'django_version': settings.DJANGO_VERSION,
            'hostname': platform.node(),
            'cpu_count': os.cpu_count(),
            'memory': self._get_memory_info(),
        }
        return success_response(system_info)
    
    def _get_memory_info(self):
        """
        获取内存信息（仅在类Unix系统上有效）
        """
        try:
            if platform.system() == 'Linux':
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                mem_info = {}
                for line in lines:
                    key, value = line.split(':')
                    mem_info[key.strip()] = value.strip()
                return {
                    'total': mem_info.get('MemTotal', 'Unknown'),
                    'free': mem_info.get('MemFree', 'Unknown'),
                    'available': mem_info.get('MemAvailable', 'Unknown'),
                }
            return {'status': 'Not supported on this platform'}
        except Exception:
            return {'status': 'Error getting memory info'} 