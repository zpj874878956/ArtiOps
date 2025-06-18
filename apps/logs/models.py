from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class LoginLog(models.Model):
    """
    登录日志表
    """
    STATUS_CHOICES = (
        ('success', _('成功')),
        ('failed', _('失败')),
    )
    
    username = models.CharField(max_length=150, verbose_name=_('用户名'))
    ip_address = models.CharField(max_length=50, verbose_name=_('IP地址'))
    user_agent = models.TextField(verbose_name=_('用户代理'), blank=True)
    login_time = models.DateTimeField(auto_now_add=True, verbose_name=_('登录时间'))
    status = models.CharField(max_length=20, verbose_name=_('状态'), choices=STATUS_CHOICES)
    message = models.TextField(verbose_name=_('消息'), blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                          verbose_name=_('用户'), related_name='login_logs')
    
    class Meta:
        verbose_name = _('登录日志')
        verbose_name_plural = _('登录日志')
        ordering = ['-login_time']
        
    def __str__(self):
        return f"{self.username} - {self.login_time}"


class OperationLog(models.Model):
    """
    操作日志表
    """
    ACTION_CHOICES = (
        ('create', _('创建')),
        ('update', _('更新')),
        ('delete', _('删除')),
        ('execute', _('执行')),
        ('login', _('登录')),
        ('logout', _('登出')),
        ('upload', _('上传')),
        ('download', _('下载')),
        ('other', _('其他')),
    )
    
    RESOURCE_TYPE_CHOICES = (
        ('project', _('项目')),
        ('environment', _('环境')),
        ('build', _('构建任务')),
        ('credential', _('凭据')),
        ('user', _('用户')),
        ('system', _('系统')),
        ('file', _('文件')),
        ('other', _('其他')),
    )
    
    STATUS_CHOICES = (
        ('success', _('成功')),
        ('failed', _('失败')),
    )
    
    username = models.CharField(max_length=150, verbose_name=_('用户名'))
    ip_address = models.CharField(max_length=50, verbose_name=_('IP地址'))
    operation_time = models.DateTimeField(auto_now_add=True, verbose_name=_('操作时间'))
    action = models.CharField(max_length=20, verbose_name=_('操作类型'), choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=20, verbose_name=_('资源类型'), choices=RESOURCE_TYPE_CHOICES)
    resource_id = models.CharField(max_length=50, verbose_name=_('资源ID'), blank=True)
    resource_name = models.CharField(max_length=255, verbose_name=_('资源名称'), blank=True)
    content = models.TextField(verbose_name=_('操作内容'), blank=True)
    status = models.CharField(max_length=20, verbose_name=_('状态'), choices=STATUS_CHOICES, default='success')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                          verbose_name=_('用户'), related_name='operation_logs')
    
    class Meta:
        verbose_name = _('操作日志')
        verbose_name_plural = _('操作日志')
        ordering = ['-operation_time']
        
    def __str__(self):
        return f"{self.username} - {self.get_action_display()} {self.resource_name} - {self.operation_time}" 