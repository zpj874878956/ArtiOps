from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """
    运维平台首页/仪表盘视图
    显示系统概览信息，包括主机数量、命令执行统计等
    """
    # 这里可以添加获取统计数据的逻辑
    # 例如：主机总数、在线主机数、命令执行次数、危险命令拦截次数等
    
    context = {
        'host_count': 42,  # 示例数据，实际应从数据库查询
        'online_host_count': 38,
        'command_template_count': 15,
        'command_execution_count': 128,
        'dangerous_command_blocked_count': 7,
    }
    
    return render(request, 'index.html', context)