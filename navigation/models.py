from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class SystemCategory(models.Model):
    """
    系统分类模型
    用于对导航系统进行分类管理
    """
    name = models.CharField(_('分类名称'), max_length=50)
    description = models.TextField(_('分类描述'), blank=True, null=True)
    icon = models.CharField(_('图标'), max_length=50, blank=True, null=True, help_text='图标名称或CSS类')
    order = models.IntegerField(_('排序'), default=0, help_text='数字越小排序越靠前')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_categories',
        verbose_name=_('创建人')
    )
    
    class Meta:
        verbose_name = _('系统分类')
        verbose_name_plural = _('系统分类')
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.name


class ExternalSystem(models.Model):
    """
    外部系统模型
    用于管理导航系统中的外部系统链接
    """
    SYSTEM_TYPE_CHOICES = (
        ('jenkins', 'Jenkins'),
        ('zabbix', 'Zabbix'),
        ('gitlab', 'GitLab'),
        ('grafana', 'Grafana'),
        ('prometheus', 'Prometheus'),
        ('kibana', 'Kibana'),
        ('kubernetes', 'Kubernetes'),
        ('custom', '自定义系统'),
    )
    
    AUTH_TYPE_CHOICES = (
        ('none', '无认证'),
        ('basic', 'Basic认证'),
        ('oauth2', 'OAuth 2.0'),
        ('token', 'API Token'),
    )
    
    STATUS_CHOICES = (
        ('online', '在线'),
        ('offline', '离线'),
        ('maintenance', '维护中'),
    )
    
    name = models.CharField(_('系统名称'), max_length=100)
    system_type = models.CharField(_('系统类型'), max_length=20, choices=SYSTEM_TYPE_CHOICES)
    category = models.ForeignKey(
        SystemCategory, 
        on_delete=models.SET_NULL, 
        related_name='systems',
        verbose_name=_('所属分类'),
        blank=True, 
        null=True
    )
    base_url = models.URLField(_('系统地址'))
    icon = models.CharField(_('图标'), max_length=50, blank=True, null=True, help_text='图标名称或CSS类')
    description = models.TextField(_('系统描述'), blank=True, null=True)
    status = models.CharField(_('状态'), max_length=20, choices=STATUS_CHOICES, default='online')
    is_active = models.BooleanField(_('是否启用'), default=True)
    
    # 认证信息
    auth_type = models.CharField(_('认证类型'), max_length=20, choices=AUTH_TYPE_CHOICES, default='none')
    auth_config = models.JSONField(_('认证配置'), default=dict, blank=True)
    
    # 排序和访问统计
    order = models.IntegerField(_('排序'), default=0, help_text='数字越小排序越靠前')
    access_count = models.IntegerField(_('访问次数'), default=0)
    score = models.FloatField(_('排序得分'), default=0.0)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_systems',
        verbose_name=_('创建人')
    )
    
    class Meta:
        verbose_name = _('外部系统')
        verbose_name_plural = _('外部系统')
        ordering = ['-score', 'order', 'id']
    
    def __str__(self):
        return self.name
    
    def calculate_score(self):
        """
        计算系统得分，用于智能排序
        结合访问次数和最后访问时间
        """
        # 基础得分为访问次数
        self.score = float(self.access_count)
        return self.score


class SystemPermission(models.Model):
    """
    系统权限模型
    用于控制不同用户或用户组对系统的访问权限
    """
    system = models.ForeignKey(
        ExternalSystem, 
        on_delete=models.CASCADE, 
        related_name='permissions',
        verbose_name=_('系统')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='system_permissions',
        verbose_name=_('用户'),
        null=True, 
        blank=True
    )
    group = models.ForeignKey(
        'auth.Group', 
        on_delete=models.CASCADE, 
        related_name='system_permissions',
        verbose_name=_('用户组'),
        null=True, 
        blank=True
    )
    can_access = models.BooleanField(_('允许访问'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('系统权限')
        verbose_name_plural = _('系统权限')
        unique_together = [
            ('system', 'user'),
            ('system', 'group'),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.system.name} - {self.user.username}"
        elif self.group:
            return f"{self.system.name} - {self.group.name}"
        return f"{self.system.name} - 未知"


class UserFavorite(models.Model):
    """
    用户收藏模型
    用于记录用户收藏的系统
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='favorites',
        verbose_name=_('用户')
    )
    system = models.ForeignKey(
        ExternalSystem, 
        on_delete=models.CASCADE, 
        related_name='favorited_by',
        verbose_name=_('系统')
    )
    created_at = models.DateTimeField(_('收藏时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('用户收藏')
        verbose_name_plural = _('用户收藏')
        unique_together = ('user', 'system')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.system.name}"


class AccessLog(models.Model):
    """
    访问日志模型
    用于记录用户对系统的访问历史
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='access_logs',
        verbose_name=_('用户')
    )
    system = models.ForeignKey(
        ExternalSystem, 
        on_delete=models.CASCADE, 
        related_name='access_logs',
        verbose_name=_('系统')
    )
    access_time = models.DateTimeField(_('访问时间'), auto_now_add=True)
    access_ip = models.GenericIPAddressField(_('访问IP'), blank=True, null=True)
    user_agent = models.TextField(_('User Agent'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('访问日志')
        verbose_name_plural = _('访问日志')
        ordering = ['-access_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.system.name} - {self.access_time}"
