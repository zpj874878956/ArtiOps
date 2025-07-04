from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    自定义用户模型，扩展Django的AbstractUser
    """
    # 用户类型选项
    USER_TYPE_CHOICES = (
        ('admin', '管理员'),
        ('operator', '运维员'),
        ('readonly', '只读用户'),
    )
    
    # 扩展字段
    user_type = models.CharField(_('用户类型'), max_length=20, choices=USER_TYPE_CHOICES, default='readonly')
    phone = models.CharField(_('手机号'), max_length=11, blank=True, null=True)
    department = models.CharField(_('部门'), max_length=50, blank=True, null=True)
    position = models.CharField(_('职位'), max_length=50, blank=True, null=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(_('最后登录IP'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        """判断是否为管理员"""
        return self.user_type == 'admin'
    
    @property
    def is_operator(self):
        """判断是否为运维员"""
        return self.user_type == 'operator'
    
    @property
    def is_readonly(self):
        """判断是否为只读用户"""
        return self.user_type == 'readonly'


class UserLoginLog(models.Model):
    """
    用户登录日志
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs', verbose_name=_('用户'))
    login_time = models.DateTimeField(_('登录时间'), auto_now_add=True)
    login_ip = models.GenericIPAddressField(_('登录IP'), blank=True, null=True)
    login_type = models.CharField(_('登录类型'), max_length=20, default='web')
    user_agent = models.TextField(_('User Agent'), blank=True, null=True)
    is_success = models.BooleanField(_('是否成功'), default=True)
    fail_reason = models.CharField(_('失败原因'), max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = _('登录日志')
        verbose_name_plural = _('登录日志')
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
