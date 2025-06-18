from django.db import models
from django.utils.translation import gettext_lazy as _


class SystemConfig(models.Model):
    """
    系统配置表
    """
    key = models.CharField(max_length=100, verbose_name=_('配置键'), unique=True)
    value = models.TextField(verbose_name=_('配置值'))
    description = models.TextField(verbose_name=_('描述'), blank=True)
    is_encrypted = models.BooleanField(default=False, verbose_name=_('是否加密'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('系统配置')
        verbose_name_plural = _('系统配置')
        ordering = ['key']
    
    def __str__(self):
        return self.key 