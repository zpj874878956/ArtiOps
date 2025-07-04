from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import CommandTemplate, CommandExecution, DangerousCommand
from .utils import CommandChecker


@login_required
def command_templates(request):
    """
    命令模板管理页面
    """
    return render(request, 'commands/command_templates.html')


@login_required
def execution_history(request):
    """
    命令执行历史页面
    """
    return render(request, 'commands/execution_history.html')


@login_required
def dangerous_commands(request):
    """
    危险命令管理页面
    """
    return render(request, 'commands/dangerous_commands.html')


@login_required
def command_checker(request):
    """
    命令安全检查工具页面
    """
    return render(request, 'commands/command_checker.html')


@login_required
@require_POST
def check_command_safety(request):
    """
    检查命令安全性的AJAX接口
    """
    command = request.POST.get('command', '')
    command_type = request.POST.get('command_type', 'shell')
    
    if not command:
        return JsonResponse({'error': '命令不能为空'}, status=400)
    
    # 使用CommandChecker检查命令安全性
    checker = CommandChecker()
    result = checker.check_command(command, command_type)
    
    return JsonResponse({
        'is_dangerous': result['is_dangerous'],
        'dangerous_commands': result['dangerous_commands'],
        'analysis': {
            'risk_level': result.get('risk_level', '未知'),
            'summary': result.get('summary', '无法分析'),
            'suggestions': result.get('suggestions', [])
        }
    })


@login_required
@require_POST
def cancel_execution(request, execution_id):
    """
    取消命令执行的AJAX接口
    """
    execution = get_object_or_404(CommandExecution, id=execution_id)
    
    # 检查权限：只有创建者或管理员可以取消
    if execution.created_by != request.user and not request.user.is_admin:
        return JsonResponse({'error': '没有权限执行此操作'}, status=403)
    
    # 检查状态：只有等待或执行中的任务可以取消
    if execution.status not in ['pending', 'running']:
        return JsonResponse({'error': f'当前状态({execution.status})的任务无法取消'}, status=400)
    
    # 更新状态
    execution.status = 'canceled'
    execution.end_time = timezone.now()
    execution.save()
    
    return JsonResponse({
        'success': True,
        'message': '任务已成功取消',
        'status': execution.status
    })