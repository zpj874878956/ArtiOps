from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Host, HostGroup, HostTag, SSHCredential
from .serializers import HostSerializer, HostGroupSerializer, HostTagSerializer, SSHCredentialSerializer


class HostGroupViewSet(viewsets.ModelViewSet):
    """主机组视图集"""
    queryset = HostGroup.objects.all()
    serializer_class = HostGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """获取查询集"""
        user = self.request.user
        # 超级用户可以查看所有主机组
        if user.is_superuser:
            return HostGroup.objects.all()
        # 普通用户只能查看自己创建的主机组
        return HostGroup.objects.filter(created_by=user)
    
    @action(detail=True, methods=['get'])
    def hosts(self, request, pk=None):
        """获取主机组中的主机列表"""
        host_group = self.get_object()
        hosts = host_group.hosts.all()
        serializer = HostSerializer(hosts, many=True)
        return Response(serializer.data)


class HostTagViewSet(viewsets.ModelViewSet):
    """主机标签视图集"""
    queryset = HostTag.objects.all()
    serializer_class = HostTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """获取查询集"""
        user = self.request.user
        # 超级用户可以查看所有标签
        if user.is_superuser:
            return HostTag.objects.all()
        # 普通用户只能查看自己创建的标签
        return HostTag.objects.filter(created_by=user)
    
    @action(detail=True, methods=['get'])
    def hosts(self, request, pk=None):
        """获取标签关联的主机列表"""
        host_tag = self.get_object()
        hosts = host_tag.hosts.all()
        serializer = HostSerializer(hosts, many=True)
        return Response(serializer.data)


class HostViewSet(viewsets.ModelViewSet):
    """主机视图集"""
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hostname', 'ip_address', 'status', 'os_type', 'groups', 'tags']
    search_fields = ['hostname', 'ip_address', 'description']
    ordering_fields = ['hostname', 'ip_address', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """获取查询集"""
        user = self.request.user
        # 超级用户可以查看所有主机
        if user.is_superuser:
            return Host.objects.all()
        # 普通用户只能查看自己创建的主机
        return Host.objects.filter(created_by=user)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索主机"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': '请提供搜索关键字'}, status=status.HTTP_400_BAD_REQUEST)
        
        hosts = self.get_queryset().filter(
            Q(hostname__icontains=query) | 
            Q(ip_address__icontains=query) | 
            Q(description__icontains=query)
        )
        
        page = self.paginate_queryset(hosts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(hosts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def credentials(self, request, pk=None):
        """获取主机关联的SSH凭证"""
        host = self.get_object()
        credentials = host.credentials.all()
        serializer = SSHCredentialSerializer(credentials, many=True)
        return Response(serializer.data)


class SSHCredentialViewSet(viewsets.ModelViewSet):
    """SSH凭证视图集"""
    queryset = SSHCredential.objects.all()
    serializer_class = SSHCredentialSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'auth_type', 'username', 'is_default']
    search_fields = ['name', 'username']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """获取查询集"""
        user = self.request.user
        # 超级用户可以查看所有凭证
        if user.is_superuser:
            return SSHCredential.objects.all()
        # 普通用户只能查看自己创建的凭证
        return SSHCredential.objects.filter(created_by=user)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """获取默认凭证"""
        default_credential = self.get_queryset().filter(is_default=True).first()
        if not default_credential:
            return Response({'error': '未设置默认凭证'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(default_credential)
        return Response(serializer.data)
