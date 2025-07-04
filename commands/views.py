from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import CommandTemplate, CommandExecution, ExecutionLog, DangerousCommand
from .serializers import (
    CommandTemplateSerializer, 
    CommandExecutionSerializer, 
    ExecutionLogSerializer, 
    DangerousCommandSerializer,
    CommandExecutionCreateSerializer
)

import re
import json
import logging

# 获取日志记录器
logger = logging.getLogger('ops_platform')


class CommandTemplateViewSet(viewsets.ModelViewSet):
    """
    命令模板视图集
    提供命令模板的CRUD操作
    """
    serializer_class = CommandTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template_type', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """
        获取查询集，根据用户权限过滤
        - 管理员可以看到所有模板
        - 普通用户只能看到自己创建的和公开的模板
        """
        user = self.request.user
        if user.is_admin:
            return CommandTemplate.objects.all()
        return CommandTemplate.objects.filter(
            Q(created_by=user) | Q(is_public=True)
        )
    
    @swagger_auto_schema(
        operation_description="获取命令模板列表",
        responses={200: CommandTemplateSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="创建新的命令模板",
        request_body=CommandTemplateSerializer,
        responses={201: CommandTemplateSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="获取指定命令模板的详细信息",
        responses={200: CommandTemplateSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="更新指定的命令模板",
        request_body=CommandTemplateSerializer,
        responses={200: CommandTemplateSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="部分更新指定的命令模板",
        request_body=CommandTemplateSerializer,
        responses={200: CommandTemplateSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="删除指定的命令模板",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CommandExecutionViewSet(viewsets.ModelViewSet):
    """
    命令执行视图集
    提供命令执行的创建、查询和管理功能
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['execution_type', 'status']
    search_fields = ['name']
    ordering_fields = ['created_at', 'start_time', 'end_time']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        根据不同的操作返回不同的序列化器
        - 创建操作使用专用的创建序列化器
        - 其他操作使用标准序列化器
        """
        if self.action == 'create':
            return CommandExecutionCreateSerializer
        return CommandExecutionSerializer
    
    def get_queryset(self):
        """
        获取查询集，根据用户权限过滤
        - 管理员可以看到所有执行记录
        - 普通用户只能看到自己创建的执行记录
        """
        user = self.request.user
        if user.is_admin:
            return CommandExecution.objects.all()
        return CommandExecution.objects.filter(created_by=user)
    
    @swagger_auto_schema(
        operation_description="获取命令执行记录列表",
        responses={200: CommandExecutionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="创建新的命令执行任务",
        request_body=CommandExecutionCreateSerializer,
        responses={201: CommandExecutionSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 检查命令是否包含危险操作
        command_content = serializer.validated_data.get('command_content', '')
        dangerous_commands = self._check_dangerous_commands(command_content)
        
        # 如果存在需要阻止的危险命令，返回错误
        blocked_commands = [cmd for cmd in dangerous_commands if cmd['action'] == 'block']
        if blocked_commands:
            return Response({
                'error': '命令包含禁止执行的危险操作',
                'dangerous_commands': blocked_commands
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建执行记录
        execution = serializer.save(created_by=request.user)
        
        # 记录警告级别的危险命令
        warn_commands = [cmd for cmd in dangerous_commands if cmd['action'] == 'warn']
        for cmd in warn_commands:
            ExecutionLog.objects.create(
                execution=execution,
                log_level='warning',
                message=f"检测到潜在危险命令: {cmd['pattern']} - {cmd['description']}"
            )
        
        # 这里应该启动异步任务执行命令，但目前只是模拟
        # 在实际项目中，应该使用Celery等异步任务队列
        self._simulate_execution(execution)
        
        return Response(CommandExecutionSerializer(execution).data, status=status.HTTP_201_CREATED)
    
    def _check_dangerous_commands(self, command_content):
        """
        检查命令是否包含危险操作
        返回匹配到的危险命令列表
        """
        result = []
        dangerous_commands = DangerousCommand.objects.all()
        
        for dc in dangerous_commands:
            if dc.command_type == 'regex':
                if re.search(dc.pattern, command_content):
                    result.append({
                        'pattern': dc.pattern,
                        'description': dc.description,
                        'action': dc.action
                    })
            elif dc.command_type == 'exact':
                if dc.pattern in command_content:
                    result.append({
                        'pattern': dc.pattern,
                        'description': dc.description,
                        'action': dc.action
                    })
        
        return result
    
    def _simulate_execution(self, execution):
        """
        模拟命令执行过程
        在实际项目中，这里应该启动真正的命令执行
        """
        # 更新状态为执行中
        execution.status = 'running'
        execution.start_time = timezone.now()
        execution.save()
        
        # 记录开始执行日志
        ExecutionLog.objects.create(
            execution=execution,
            log_level='info',
            message=f"开始执行{execution.execution_type}命令"
        )
        
        # 在实际项目中，这里应该异步执行命令
        # 为了演示，我们直接模拟执行结果
        execution.status = 'completed'
        execution.end_time = timezone.now()
        execution.result = {
            'success': True,
            'message': '命令执行成功',
            'hosts_result': {
                'success': 3,
                'failed': 0,
                'total': 3
            }
        }
        execution.save()
        
        # 记录执行完成日志
        ExecutionLog.objects.create(
            execution=execution,
            log_level='info',
            message=f"命令执行完成，成功率: 100%"
        )
    
    @swagger_auto_schema(
        operation_description="获取指定命令执行记录的详细信息",
        responses={200: CommandExecutionSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="获取指定命令执行记录的日志",
        responses={200: ExecutionLogSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        获取指定命令执行记录的日志
        """
        execution = self.get_object()
        logs = ExecutionLog.objects.filter(execution=execution)
        serializer = ExecutionLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="取消正在执行的命令",
        responses={200: CommandExecutionSerializer}
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        取消正在执行的命令
        """
        execution = self.get_object()
        
        # 只有处于等待或执行中状态的任务才能取消
        if execution.status not in ['pending', 'running']:
            return Response({
                'error': f"当前状态({execution.status})的任务无法取消"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新状态为已取消
        execution.status = 'canceled'
        execution.end_time = timezone.now()
        execution.save()
        
        # 记录取消日志
        ExecutionLog.objects.create(
            execution=execution,
            log_level='warning',
            message=f"任务被用户{request.user.username}手动取消"
        )
        
        # 在实际项目中，这里应该发送信号给异步任务，通知其停止执行
        
        return Response(CommandExecutionSerializer(execution).data)
    
    @swagger_auto_schema(
        operation_description="重新执行指定的命令",
        responses={200: CommandExecutionSerializer}
    )
    @action(detail=True, methods=['post'])
    def rerun(self, request, pk=None):
        """
        重新执行指定的命令
        """
        old_execution = self.get_object()
        
        # 创建新的执行记录
        new_execution = CommandExecution.objects.create(
            name=f"重新执行: {old_execution.name}",
            execution_type=old_execution.execution_type,
            command_content=old_execution.command_content,
            template=old_execution.template,
            target_hosts=old_execution.target_hosts,
            parameters=old_execution.parameters,
            created_by=request.user
        )
        
        # 记录关联日志
        ExecutionLog.objects.create(
            execution=new_execution,
            log_level='info',
            message=f"这是对任务 {old_execution.id} 的重新执行"
        )
        
        # 模拟执行
        self._simulate_execution(new_execution)
        
        return Response(CommandExecutionSerializer(new_execution).data)


class DangerousCommandViewSet(viewsets.ModelViewSet):
    """
    危险命令视图集
    提供危险命令的CRUD操作
    """
    queryset = DangerousCommand.objects.all()
    serializer_class = DangerousCommandSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['command_type', 'action']
    search_fields = ['pattern', 'description']
    
    def get_permissions(self):
        """
        权限控制：只有管理员可以管理危险命令
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="获取危险命令列表",
        responses={200: DangerousCommandSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="创建新的危险命令",
        request_body=DangerousCommandSerializer,
        responses={201: DangerousCommandSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="获取指定危险命令的详细信息",
        responses={200: DangerousCommandSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="更新指定的危险命令",
        request_body=DangerousCommandSerializer,
        responses={200: DangerousCommandSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="部分更新指定的危险命令",
        request_body=DangerousCommandSerializer,
        responses={200: DangerousCommandSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="删除指定的危险命令",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="检查命令是否包含危险操作",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['command'],
            properties={
                'command': openapi.Schema(type=openapi.TYPE_STRING, description='要检查的命令')
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'is_dangerous': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否包含危险操作'),
                    'dangerous_commands': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'pattern': openapi.Schema(type=openapi.TYPE_STRING),
                                'description': openapi.Schema(type=openapi.TYPE_STRING),
                                'action': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    )
                }
            )
        }
    )
    @action(detail=False, methods=['post'])
    def check_command(self, request):
        """
        检查命令是否包含危险操作
        """
        command = request.data.get('command', '')
        if not command:
            return Response({'error': '命令不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查命令是否包含危险操作
        dangerous_commands = []
        for dc in DangerousCommand.objects.all():
            if dc.command_type == 'regex':
                if re.search(dc.pattern, command):
                    dangerous_commands.append({
                        'pattern': dc.pattern,
                        'description': dc.description,
                        'action': dc.action
                    })
            elif dc.command_type == 'exact':
                if dc.pattern in command:
                    dangerous_commands.append({
                        'pattern': dc.pattern,
                        'description': dc.description,
                        'action': dc.action
                    })
        
        return Response({
            'is_dangerous': len(dangerous_commands) > 0,
            'dangerous_commands': dangerous_commands
        })


class ExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    执行日志视图集
    提供执行日志的只读操作
    """
    serializer_class = ExecutionLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['execution', 'log_level']
    ordering_fields = ['timestamp']
    ordering = ['timestamp']
    
    def get_queryset(self):
        """
        获取查询集，根据用户权限过滤
        - 管理员可以看到所有日志
        - 普通用户只能看到自己创建的执行记录的日志
        """
        user = self.request.user
        if user.is_admin:
            return ExecutionLog.objects.all()
        return ExecutionLog.objects.filter(execution__created_by=user)
    
    @swagger_auto_schema(
        operation_description="获取执行日志列表",
        responses={200: ExecutionLogSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="获取指定执行日志的详细信息",
        responses={200: ExecutionLogSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
