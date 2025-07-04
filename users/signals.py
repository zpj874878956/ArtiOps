from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_login_failed

from .models import User, UserLoginLog


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    用户登录成功信号处理
    """
    # 登录成功日志在视图中处理，这里不再重复记录
    pass


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """
    用户登录失败信号处理
    """
    # 获取登录失败的用户名
    username = credentials.get('username', '')
    
    # 尝试获取用户
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # 用户不存在，无法记录具体用户的登录失败日志
        return
    
    # 记录登录失败日志
    UserLoginLog.objects.create(
        user=user,
        login_ip=get_client_ip(request),
        login_type='web',
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        is_success=False
    )


def get_client_ip(request):
    """
    获取客户端IP
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip