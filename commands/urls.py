from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CommandTemplateViewSet,
    CommandExecutionViewSet,
    DangerousCommandViewSet,
    ExecutionLogViewSet
)
from .page_views import (
    command_templates,
    execution_history,
    dangerous_commands,
    command_checker,
    check_command_safety,
    cancel_execution
)

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'api/templates', CommandTemplateViewSet, basename='command-template')
router.register(r'api/executions', CommandExecutionViewSet, basename='command-execution')
router.register(r'api/dangerous-commands', DangerousCommandViewSet, basename='dangerous-command')
router.register(r'api/logs', ExecutionLogViewSet, basename='execution-log')

# URL配置
urlpatterns = [
    # API接口
    path('api/', include(router.urls)),
    
    # 页面视图
    path('templates/', command_templates, name='command_templates'),
    path('executions/', execution_history, name='execution_history'),
    path('dangerous-commands/', dangerous_commands, name='dangerous_commands'),
    path('checker/', command_checker, name='command_checker'),
    
    # AJAX接口
    path('check-command/', check_command_safety, name='check_command_safety'),
    path('executions/<uuid:execution_id>/cancel/', cancel_execution, name='cancel_execution'),
]