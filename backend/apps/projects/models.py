from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Project(models.Model):
    """
    项目表
    """
    name = models.CharField(max_length=100, verbose_name=_('项目名称'))
    key = models.CharField(max_length=50, verbose_name=_('项目标识'), unique=True)
    description = models.TextField(verbose_name=_('项目描述'), blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('负责人'), 
                            related_name='owned_projects')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                verbose_name=_('创建人'), related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('项目')
        verbose_name_plural = _('项目')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    """
    项目成员表
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_('项目'), 
                              related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('用户'), 
                           related_name='project_memberships')
    role = models.CharField(max_length=50, verbose_name=_('项目角色'), 
                          choices=(
                              ('manager', _('管理员')),
                              ('developer', _('开发者')),
                              ('viewer', _('观察者')),
                          ), default='developer')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    
    class Meta:
        verbose_name = _('项目成员')
        verbose_name_plural = _('项目成员')
        unique_together = ('project', 'user')
    
    def __str__(self):
        return f"{self.project.name} - {self.user.username}" 