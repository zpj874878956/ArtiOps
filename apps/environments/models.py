from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.projects.models import Project


class Environment(models.Model):
    """
    环境表
    """
    TYPE_CHOICES = (
        ('dev', _('开发环境')),
        ('test', _('测试环境')),
        ('staging', _('预生产环境')),
        ('prod', _('生产环境')),
    )
    
    name = models.CharField(max_length=100, verbose_name=_('环境名称'))
    type = models.CharField(max_length=20, verbose_name=_('环境类型'), choices=TYPE_CHOICES)
    description = models.TextField(verbose_name=_('环境描述'), blank=True)
    api_endpoint = models.URLField(verbose_name=_('API端点'), blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_('所属项目'),
                             related_name='environments')
    variables = models.JSONField(verbose_name=_('环境变量'), default=dict, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                verbose_name=_('创建人'), related_name='created_environments')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('环境')
        verbose_name_plural = _('环境')
        ordering = ['id']
        unique_together = ('name', 'project')
    
    def __str__(self):
        return f"{self.project.name} - {self.name}" 