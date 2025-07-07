from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Host, HostGroup, HostTag, SSHCredential
from .serializers import (
    HostSerializer, HostGroupSerializer, HostTagSerializer, 
    SSHCredentialSerializer, SSHCredentialCreateSerializer
)


class SSHCredentialViewSet(viewsets.ModelViewSet):
    """
    SSH凭证管理的API视图集
    """
    queryset = SSHCredential.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SSHCredentialCreateSerializer
        return SSHCredentialSerializer
    
    def get_queryset(self):
        # 普通用户只能查看自己创建的凭证
        user = self.request.user
        if not user.is_admin:
            return self.queryset.filter(created_by=user)
        return self.queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @swagger_auto_schema(
        operation_description="测试SSH凭证连接",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'host_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='主机ID'),
            },
            required=['host_id']
        ),
        responses={200: openapi.Response('测试结果', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否成功'),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='结果消息'),
            }
        ))}
    )
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        测试SSH凭证连接
        """
        credential = self.get_object()
        host_id = request.data.get('host_id')
        
        if not host_id:
            return Response({'error': '主机ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        host = get_object_or_404(Host, id=host_id)
        
        # 检查权限
        if host.created_by != request.user and not request.user.is_admin:
            return Response({'error': '没有权限执行此操作'}, status=status.HTTP_403_FORBIDDEN)
        
        # 模拟SSH连接测试
        # 在实际项目中，这里应该使用paramiko等库进行真正的SSH连接测试
        success = True  # 假设连接成功
        message = '连接成功' if success else '连接失败'
        
        return Response({
            'success': success,
            'message': message
        })


@login_required
@require_GET
def get_ssh_credentials(request):
    """
    获取SSH凭证列表的AJAX接口
    """
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '')
    
    # 构建查询集
    queryset = SSHCredential.objects.all()
    
    # 普通用户只能查看自己创建的凭证
    if not request.user.is_admin:
        queryset = queryset.filter(created_by=request.user)
    
    # 搜索过滤
    if search:
        queryset = queryset.filter(name__icontains=search) | queryset.filter(username__icontains=search)
    
    # 添加关联主机数量
    queryset = queryset.annotate(host_count=Count('hosts'))
    
    # 分页
    paginator = Paginator(queryset, 10)
    credentials = paginator.get_page(page)
    
    # 构建响应数据
    data = {
        'total': paginator.count,
        'page': int(page),
        'total_pages': paginator.num_pages,
        'credentials': []
    }
    
    for credential in credentials:
        data['credentials'].append({
            'id': credential.id,
            'name': credential.name,
            'username': credential.username,
            'auth_type': credential.get_auth_type_display(),
            'host_count': credential.host_count,
            'created_by': credential.created_by.username if credential.created_by else 'Unknown',
            'created_at': credential.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse(data)


@login_required
@require_GET
def get_credential_detail(request, credential_id):
    """
    获取SSH凭证详情的AJAX接口
    """
    credential = get_object_or_404(SSHCredential, id=credential_id)
    
    # 检查权限
    if credential.created_by != request.user and not request.user.is_admin:
        return JsonResponse({'error': '没有权限查看此凭证'}, status=403)
    
    # 构建响应数据
    data = {
        'id': credential.id,
        'name': credential.name,
        'username': credential.username,
        'auth_type': credential.get_auth_type_display(),
        'is_default': credential.is_default,
        'created_by': credential.created_by.username if credential.created_by else 'Unknown',
        'created_at': credential.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': credential.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'hosts': []
    }
    
    # 获取关联主机信息
    for host in credential.hosts.all():
        data['hosts'].append({
            'id': host.id,
            'hostname': host.hostname,
            'ip_address': host.ip_address,
            'status': host.get_status_display(),
            'os_type': host.os_type or 'Unknown'
        })
    
    return JsonResponse(data)


@login_required
@require_POST
def delete_credential(request, credential_id):
    """
    删除SSH凭证的AJAX接口
    """
    credential = get_object_or_404(SSHCredential, id=credential_id)
    
    # 检查权限
    if credential.created_by != request.user and not request.user.is_admin:
        return JsonResponse({'error': '没有权限删除此凭证'}, status=403)
    
    credential_name = credential.name
    credential.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'凭证 {credential_name} 已成功删除'
    })