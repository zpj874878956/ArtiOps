from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """
    用户角色表
    """
    name = models.CharField(max_length=50, verbose_name=_('角色名称'), unique=True)
    key = models.CharField(max_length=50, verbose_name=_('角色标识'), unique=True)
    permissions = models.JSONField(verbose_name=_('权限配置'), default=dict, blank=True)
    description = models.TextField(verbose_name=_('角色描述'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name = _('角色')
        verbose_name_plural = _('角色')
        ordering = ['id']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    用户表
    """
    real_name = models.CharField(max_length=50, verbose_name=_('真实姓名'), blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, 
                            verbose_name=_('用户角色'), related_name='users')
    phone = models.CharField(max_length=20, verbose_name=_('手机号'), blank=True)
    status = models.BooleanField(default=True, verbose_name=_('状态'))
    last_login_ip = models.GenericIPAddressField(verbose_name=_('最后登录IP'), null=True, blank=True)
    last_login_time = models.DateTimeField(verbose_name=_('最后登录时间'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['id']

    def __str__(self):
        return self.username 