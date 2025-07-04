from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Host, HostGroup, HostTag, SSHCredential


@login_required
def host_list(request):
    """
    主机列表页面
    """
    return render(request, 'hosts/host_list.html')


@login_required
def host_group_list(request):
    """
    主机组列表页面
    """
    return render(request, 'hosts/host_group_list.html')


@login_required
def host_tag_list(request):
    """
    主机标签列表页面
    """
    return render(request, 'hosts/host_tag_list.html')


@login_required
def ssh_credential_list(request):
    """
    SSH凭证列表页面
    """
    return render(request, 'hosts/ssh_credential_list.html')


@login_required
def host_detail(request, host_id):
    """
    主机详情页面
    """
    host = get_object_or_404(Host, id=host_id)
    
    # 检查权限：只有创建者或管理员可以查看
    if host.created_by != request.user and not request.user.is_admin:
        messages.error(request, '没有权限查看此主机')
        return redirect('host_list')
    
    return render(request, 'hosts/host_detail.html', {'host': host})


@login_required
@require_POST
def test_ssh_connection(request):
    """
    测试SSH连接的AJAX接口
    """
    host_id = request.POST.get('host_id')
    credential_id = request.POST.get('credential_id')
    
    if not host_id or not credential_id:
        return JsonResponse({'error': '主机ID和凭证ID不能为空'}, status=400)
    
    host = get_object_or_404(Host, id=host_id)
    credential = get_object_or_404(SSHCredential, id=credential_id)
    
    # 检查权限
    if host.created_by != request.user and not request.user.is_admin:
        return JsonResponse({'error': '没有权限执行此操作'}, status=403)
    
    # 模拟SSH连接测试
    # 在实际项目中，这里应该使用paramiko等库进行真正的SSH连接测试
    success = True  # 假设连接成功
    message = '连接成功' if success else '连接失败'
    
    return JsonResponse({
        'success': success,
        'message': message
    })