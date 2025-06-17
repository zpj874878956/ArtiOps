from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.projects.models import Project
from apps.credentials.models import Credential


class BuildTask(models.Model):
    """
    构建任务表
    """
    STATUS_CHOICES = (
        ('pending', _('等待中')),
        ('running', _('运行中')),
        ('success', _('成功')),
        ('failed', _('失败')),
        ('cancelled', _('已取消')),
    )
    
    name = models.CharField(max_length=100, verbose_name=_('任务名称'))
    description = models.TextField(verbose_name=_('任务描述'), blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_('所属项目'),
                               related_name='build_tasks')
    command = models.TextField(verbose_name=_('执行命令'))
    parameters = models.JSONField(verbose_name=_('命令参数'), default=dict, blank=True)
    environment_variables = models.JSONField(verbose_name=_('环境变量'), default=dict, blank=True)
    status = models.CharField(max_length=20, verbose_name=_('状态'), choices=STATUS_CHOICES, default='pending')
    is_scheduled = models.BooleanField(default=False, verbose_name=_('是否定时任务'))
    schedule = models.CharField(max_length=100, verbose_name=_('定时计划'), blank=True,
                              help_text=_('Cron表达式，如: 0 0 * * *'))
    timeout = models.IntegerField(default=1800, verbose_name=_('超时时间(秒)'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 verbose_name=_('创建人'), related_name='created_build_tasks')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('构建任务')
        verbose_name_plural = _('构建任务')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name


class BuildHistory(models.Model):
    """
    构建历史表
    """
    STATUS_CHOICES = (
        ('running', _('运行中')),
        ('success', _('成功')),
        ('failed', _('失败')),
        ('cancelled', _('已取消')),
    )
    
    task = models.ForeignKey(BuildTask, on_delete=models.CASCADE, verbose_name=_('所属任务'),
                           related_name='build_histories')
    build_number = models.IntegerField(verbose_name=_('构建编号'))
    status = models.CharField(max_length=20, verbose_name=_('状态'), choices=STATUS_CHOICES, default='running')
    execution_path = models.CharField(max_length=255, verbose_name=_('执行路径'), blank=True)
    log_file = models.CharField(max_length=255, verbose_name=_('日志文件'), blank=True)
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('开始时间'))
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name=_('完成时间'))
    duration = models.IntegerField(default=0, verbose_name=_('持续时间(秒)'))
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  verbose_name=_('执行人'), related_name='executed_builds')
    
    class Meta:
        verbose_name = _('构建历史')
        verbose_name_plural = _('构建历史')
        ordering = ['-started_at']
        unique_together = ('task', 'build_number')
        
    def __str__(self):
        return f"{self.task.name} #{self.build_number}" 