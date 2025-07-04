from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class CommandTemplate(models.Model):
    """
    命令模板模型
    用于存储常用的命令模板，方便用户快速调用
    """
    TEMPLATE_TYPE_CHOICES = (
        ('shell', 'Shell命令'),
        ('ansible', 'Ansible Playbook'),
    )
    
    name = models.CharField(_('模板名称'), max_length=100)
    template_type = models.CharField(_('模板类型'), max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    content = models.TextField(_('模板内容'))
    description = models.TextField(_('模板描述'), blank=True, null=True)
    is_public = models.BooleanField(_('是否公开'), default=False, help_text='公开的模板所有用户可见')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='command_templates',
        verbose_name=_('创建人')
    )
    
    class Meta:
        verbose_name = _('命令模板')
        verbose_name_plural = _('命令模板')
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class CommandExecution(models.Model):
    """
    命令执行记录模型
    用于记录用户执行的命令及其结果
    """
    STATUS_CHOICES = (
        ('pending', '等待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '执行失败'),
        ('timeout', '执行超时'),
        ('canceled', '已取消'),
    )
    
    EXECUTION_TYPE_CHOICES = (
        ('shell', 'Shell命令'),
        ('ansible', 'Ansible Playbook'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('任务名称'), max_length=100)
    execution_type = models.CharField(_('执行类型'), max_length=20, choices=EXECUTION_TYPE_CHOICES)
    command_content = models.TextField(_('命令内容'))
    template = models.ForeignKey(
        CommandTemplate, 
        on_delete=models.SET_NULL, 
        related_name='executions',
        verbose_name=_('关联模板'),
        blank=True, 
        null=True
    )
    target_hosts = models.JSONField(_('目标主机'), help_text='存储主机ID列表或主机选择条件')
    parameters = models.JSONField(_('执行参数'), default=dict, blank=True, help_text='存储并发数、超时时间等参数')
    result = models.JSONField(_('执行结果'), null=True, blank=True)
    status = models.CharField(_('执行状态'), max_length=20, choices=STATUS_CHOICES, default='pending')
    start_time = models.DateTimeField(_('开始时间'), null=True, blank=True)
    end_time = models.DateTimeField(_('结束时间'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='command_executions',
        verbose_name=_('执行人')
    )
    
    class Meta:
        verbose_name = _('命令执行记录')
        verbose_name_plural = _('命令执行记录')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ExecutionLog(models.Model):
    """
    执行日志模型
    用于记录命令执行过程中的详细日志
    """
    LOG_LEVEL_CHOICES = (
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('debug', '调试'),
    )
    
    execution = models.ForeignKey(
        CommandExecution, 
        on_delete=models.CASCADE, 
        related_name='logs',
        verbose_name=_('执行记录')
    )
    host = models.CharField(_('主机'), max_length=100, blank=True, null=True)
    log_level = models.CharField(_('日志级别'), max_length=10, choices=LOG_LEVEL_CHOICES, default='info')
    message = models.TextField(_('日志内容'))
    timestamp = models.DateTimeField(_('记录时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('执行日志')
        verbose_name_plural = _('执行日志')
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.execution.name} - {self.timestamp}"


class DangerousCommand(models.Model):
    """
    危险命令模型
    用于定义需要特殊处理的危险命令
    """
    COMMAND_TYPE_CHOICES = (
        ('regex', '正则表达式'),
        ('exact', '精确匹配'),
    )
    
    pattern = models.CharField(_('命令模式'), max_length=200)
    command_type = models.CharField(_('匹配类型'), max_length=10, choices=COMMAND_TYPE_CHOICES, default='regex')
    description = models.TextField(_('危险说明'), blank=True, null=True)
    action = models.CharField(_('处理动作'), max_length=20, choices=(
        ('block', '禁止执行'),
        ('warn', '警告后执行'),
        ('log', '仅记录日志'),
    ), default='warn')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='dangerous_commands',
        verbose_name=_('创建人')
    )
    
    class Meta:
        verbose_name = _('危险命令')
        verbose_name_plural = _('危险命令')
    
    def __str__(self):
        return self.pattern
