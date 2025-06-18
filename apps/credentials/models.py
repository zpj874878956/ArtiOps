from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from core.encryption import AESCipher

class Credential(models.Model):
    """
    凭据表
    """
    TYPE_CHOICES = (
        ('ssh_key', _('SSH密钥')),
        ('username_password', _('用户名密码')),
        ('api_key', _('API密钥')),
        ('token', _('访问令牌')),
        ('certificate', _('证书')),
        ('other', _('其他')),
    )
    
    name = models.CharField(max_length=100, verbose_name=_('凭据名称'))
    credential_type = models.CharField(max_length=20, verbose_name=_('凭据类型'), choices=TYPE_CHOICES)
    description = models.TextField(verbose_name=_('凭据描述'), blank=True)
    username = models.CharField(max_length=100, verbose_name=_('用户名'), blank=True)
    password = models.TextField(verbose_name=_('密码'), blank=True)
    private_key = models.TextField(verbose_name=_('私钥'), blank=True)
    key_passphrase = models.TextField(verbose_name=_('密钥口令'), blank=True)
    token = models.TextField(verbose_name=_('令牌'), blank=True)
    extra_data = models.JSONField(verbose_name=_('额外数据'), default=dict, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('创建人'),
                                related_name='credentials')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    expires_at = models.DateTimeField(verbose_name=_('过期时间'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('凭据')
        verbose_name_plural = _('凭据')
        ordering = ['id']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """
        保存前加密敏感信息
        """
        cipher = AESCipher()
        
        # 加密敏感字段
        if self.password:
            self.password = cipher.encrypt(self.password)
        if self.private_key:
            self.private_key = cipher.encrypt(self.private_key)
        if self.key_passphrase:
            self.key_passphrase = cipher.encrypt(self.key_passphrase)
        if self.token:
            self.token = cipher.encrypt(self.token)
            
        super().save(*args, **kwargs)
    
    def get_password(self):
        """
        获取解密后的密码
        """
        if not self.password:
            return None
        return AESCipher().decrypt(self.password)
    
    def get_private_key(self):
        """
        获取解密后的私钥
        """
        if not self.private_key:
            return None
        return AESCipher().decrypt(self.private_key)
    
    def get_key_passphrase(self):
        """
        获取解密后的密钥口令
        """
        if not self.key_passphrase:
            return None
        return AESCipher().decrypt(self.key_passphrase)
    
    def get_token(self):
        """
        获取解密后的令牌
        """
        if not self.token:
            return None
        return AESCipher().decrypt(self.token)


class CredentialUsageLog(models.Model):
    """
    凭据使用日志表
    """
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE, verbose_name=_('凭据'),
                                 related_name='usage_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('使用者'),
                          related_name='credential_usages')
    ip_address = models.CharField(max_length=50, verbose_name=_('IP地址'), blank=True)
    used_at = models.DateTimeField(auto_now_add=True, verbose_name=_('使用时间'))
    action = models.CharField(max_length=100, verbose_name=_('操作'), blank=True)
    task_info = models.JSONField(verbose_name=_('任务信息'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('凭据使用日志')
        verbose_name_plural = _('凭据使用日志')
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.credential.name} - {self.used_at}" 