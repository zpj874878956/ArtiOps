"""
日志中间件
"""
import json
import logging
from .models import OperationLog
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
import re
import time

logger = logging.getLogger('apps')

class AuditLogMiddleware:
    """
    审计日志中间件，记录用户操作
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 不需要记录日志的路径
        self.exclude_paths = [
            '/api/v1/logs/',  # 日志相关API不记录，避免循环
            '/admin/jsi18n/',  # 国际化不记录
            '/static/',  # 静态文件不记录
            '/media/',  # 媒体文件不记录
            '/favicon.ico',  # 图标不记录
            '/swagger/',  # API文档不记录
            '/redoc/',  # API文档不记录
        ]
        # 不需要记录请求体的路径
        self.exclude_body_paths = [
            '/api/v1/users/login/',  # 登录不记录请求体，避免泄露密码
            '/api/v1/users/reset-password/',  # 重置密码不记录请求体
            '/api/v1/credentials/',  # 凭据不记录请求体，避免泄露敏感信息
        ]
        
    def __call__(self, request):
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取响应
        response = self.get_response(request)
        
        # 计算请求耗时
        duration = time.time() - start_time
        
        # 记录审计日志
        self._log_request(request, response, duration)
        
        return response
    
    def _log_request(self, request, response, duration):
        """记录请求日志"""
        # 检查是否需要记录
        path = request.path
        
        # 跳过不需要记录的路径
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return
        
        # 获取用户信息
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        username = user.username if user else 'anonymous'
        
        # 获取IP地址
        ip_address = self._get_client_ip(request)
        
        # 获取请求方法和路径
        method = request.method
        
        # 解析请求体
        request_body = None
        if method in ['POST', 'PUT', 'PATCH'] and request.content_type == 'application/json':
            # 检查是否需要排除请求体
            should_log_body = True
            for exclude_path in self.exclude_body_paths:
                if path.startswith(exclude_path):
                    should_log_body = False
                    break
            
            if should_log_body:
                try:
                    request_body = json.loads(request.body.decode('utf-8')) if request.body else None
                except (json.JSONDecodeError, UnicodeDecodeError):
                    request_body = "无法解析的请求体"
        
        # 获取请求参数
        query_params = dict(request.GET)
        
        # 获取状态码
        status_code = getattr(response, 'status_code', 0)
        
        # 确定操作类型
        action = self._determine_action(method)
        
        # 确定资源类型和ID
        resource_type, resource_id, resource_name = self._determine_resource(path)
        
        # 构建操作内容
        content = {
            'method': method,
            'path': path,
            'query_params': query_params,
            'request_body': request_body,
            'status_code': status_code,
            'duration': f"{duration:.3f}s",
        }
        
        # 记录日志
        try:
            OperationLog.objects.create(
                username=username,
                ip_address=ip_address,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=resource_name,
                content=json.dumps(content, ensure_ascii=False),
                status='success' if 200 <= status_code < 400 else 'failed',
                user=user,
            )
        except Exception as e:
            # 记录日志失败不应影响正常流程
            print(f"记录审计日志失败: {str(e)}")
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _determine_action(self, method):
        """根据HTTP方法确定操作类型"""
        method_action_map = {
            'GET': 'view',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }
        return method_action_map.get(method, 'other')
    
    def _determine_resource(self, path):
        """确定资源类型和ID"""
        # 默认值
        resource_type = 'other'
        resource_id = ''
        resource_name = path
        
        # 解析路径
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'api':
            if len(parts) >= 3:
                # 提取资源类型
                resource_type_map = {
                    'users': 'user',
                    'projects': 'project',
                    'builds': 'build',
                    'environments': 'environment',
                    'credentials': 'credential',
                    'system': 'system',
                }
                resource_type = resource_type_map.get(parts[2], 'other')
                
                # 提取资源ID
                if len(parts) >= 4 and parts[3].isdigit():
                    resource_id = parts[3]
        
        return resource_type, resource_id, resource_name 