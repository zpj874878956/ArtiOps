from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.utils import timezone
from django.conf import settings
from django.db import models
from .models import BuildTask, BuildHistory
from .serializers import BuildTaskSerializer, BuildTaskDetailSerializer, BuildHistorySerializer, BuildHistoryDetailSerializer
from core.permissions import RoleBasedPermission, HasBuildAccess
from core.response import success_response, error_response
import os
import subprocess
import threading
import time


class BuildTaskViewSet(viewsets.ModelViewSet):
    """
    构建任务视图集
    """
    queryset = BuildTask.objects.all()
    serializer_class = BuildTaskSerializer
    filterset_fields = ['name', 'project', 'status', 'is_scheduled']
    search_fields = ['name', 'description', 'command']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create']:
            return [RoleBasedPermission('build_create')]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [HasBuildAccess()]
        return [RoleBasedPermission('build_view')]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BuildTaskDetailSerializer
        return BuildTaskSerializer
    
    def get_queryset(self):
        user = self.request.user
        # 超级管理员可以看到所有任务
        if user.is_superuser:
            return BuildTask.objects.all()
            
        # 普通用户只能看到自己创建的任务或有权限的项目的任务
        return BuildTask.objects.filter(
            models.Q(created_by=user) | 
            models.Q(project__owner=user) | 
            models.Q(project__members__user=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """
        执行构建任务
        """
        task = self.get_object()
        
        # 检查任务状态
        if task.status in ['running', 'pending']:
            return error_response(message='任务已在运行或等待中', code=400)
        
        # 更新任务状态
        task.status = 'pending'
        task.save(update_fields=['status'])
        
        # 创建构建历史记录
        build_number = BuildHistory.objects.filter(task=task).count() + 1
        history = BuildHistory.objects.create(
            task=task,
            build_number=build_number,
            status='running',
            executed_by=request.user
        )
        
        # 异步执行任务
        threading.Thread(target=self._execute_build, args=(task, history)).start()
        
        return success_response({
            'task_id': task.id,
            'build_id': history.id,
            'build_number': build_number,
            'status': 'pending'
        }, message='任务已开始执行')
    
    def _execute_build(self, task, history):
        """
        执行构建任务（异步）
        """
        # 更新任务状态
        task.status = 'running'
        task.save(update_fields=['status'])
        
        # 创建执行目录
        execution_dir = os.path.join(settings.MEDIA_ROOT, 'builds', f'task_{task.id}', f'build_{history.build_number}')
        os.makedirs(execution_dir, exist_ok=True)
        
        # 设置日志文件
        log_file = os.path.join(execution_dir, 'build.log')
        history.execution_path = execution_dir
        history.log_file = log_file
        history.save(update_fields=['execution_path', 'log_file'])
        
        # 准备环境变量
        env = os.environ.copy()
        env.update(task.environment_variables)
        
        # 执行命令
        start_time = time.time()
        success = False
        
        try:
            with open(log_file, 'w') as f:
                f.write(f"=== 开始执行任务: {task.name} (构建 #{history.build_number}) ===\n")
                f.write(f"命令: {task.command}\n")
                f.write(f"参数: {task.parameters}\n")
                f.write(f"执行时间: {timezone.now()}\n\n")
                
                # 执行命令
                process = subprocess.Popen(
                    task.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=env,
                    cwd=execution_dir
                )
                
                # 实时读取输出并写入日志
                for line in process.stdout:
                    decoded_line = line.decode('utf-8', errors='replace')
                    f.write(decoded_line)
                    f.flush()
                
                # 等待进程结束
                return_code = process.wait()
                success = return_code == 0
                
                # 记录结果
                f.write(f"\n=== 任务执行完成 ===\n")
                f.write(f"返回码: {return_code}\n")
                f.write(f"状态: {'成功' if success else '失败'}\n")
                f.write(f"结束时间: {timezone.now()}\n")
        
        except Exception as e:
            # 记录异常
            with open(log_file, 'a') as f:
                f.write(f"\n=== 执行出错 ===\n")
                f.write(f"错误: {str(e)}\n")
                f.write(f"结束时间: {timezone.now()}\n")
        
        # 计算执行时间
        end_time = time.time()
        duration = int(end_time - start_time)
        
        # 更新构建历史
        history.status = 'success' if success else 'failed'
        history.finished_at = timezone.now()
        history.duration = duration
        history.save(update_fields=['status', 'finished_at', 'duration'])
        
        # 更新任务状态
        task.status = 'success' if success else 'failed'
        task.save(update_fields=['status'])


class BuildHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    构建历史视图集（只读）
    """
    queryset = BuildHistory.objects.all()
    serializer_class = BuildHistorySerializer
    filterset_fields = ['task', 'status', 'executed_by']
    ordering_fields = ['id', 'build_number', 'started_at', 'duration']
    ordering = ['-started_at']
    
    def get_permissions(self):
        return [RoleBasedPermission('build_view')]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BuildHistoryDetailSerializer
        return BuildHistorySerializer
    
    def get_queryset(self):
        user = self.request.user
        # 超级管理员可以看到所有历史
        if user.is_superuser:
            return BuildHistory.objects.all()
            
        # 普通用户只能看到自己执行的或有权限的项目的历史
        return BuildHistory.objects.filter(
            models.Q(executed_by=user) | 
            models.Q(task__created_by=user) | 
            models.Q(task__project__owner=user) | 
            models.Q(task__project__members__user=user)
        ).distinct()
    
    @action(detail=True, methods=['get'])
    def log(self, request, pk=None):
        """
        获取构建日志
        """
        history = self.get_object()
        
        if not history.log_file or not os.path.exists(history.log_file):
            return error_response(message='日志文件不存在', code=404)
        
        try:
            with open(history.log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            return success_response({'log': log_content})
        except Exception as e:
            return error_response(message=f'读取日志文件失败: {str(e)}', code=500) 