from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class HostGroup(models.Model):
    """主机组模型"""
    name = models.CharField(max_length=100, verbose_name='组名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '主机组'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Host(models.Model):
    """主机模型"""
    STATUS_CHOICES = (
        ('online', '在线'),
        ('offline', '离线'),
        ('unknown', '未知'),
        ('maintenance', '维护中'),
    )
    
    hostname = models.CharField(max_length=100, verbose_name='主机名')
    ip_address = models.CharField(max_length=100, verbose_name='IP地址')
    port = models.IntegerField(default=22, verbose_name='SSH端口')
    os_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='操作系统类型')
    os_version = models.CharField(max_length=50, blank=True, null=True, verbose_name='操作系统版本')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown', verbose_name='状态')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    groups = models.ManyToManyField(HostGroup, blank=True, related_name='hosts', verbose_name='所属组')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '主机'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ('hostname', 'ip_address')
    
    def __str__(self):
        return f'{self.hostname} ({self.ip_address})'


class HostTag(models.Model):
    """主机标签模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名')
    color = models.CharField(max_length=20, default='#1890ff', verbose_name='标签颜色')
    hosts = models.ManyToManyField(Host, blank=True, related_name='tags', verbose_name='关联主机')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '主机标签'
        verbose_name_plural = verbose_name
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SSHCredential(models.Model):
    """SSH凭证模型"""
    AUTH_TYPE_CHOICES = (
        ('password', '密码'),
        ('key', '密钥'),
    )
    
    name = models.CharField(max_length=100, verbose_name='凭证名称')
    auth_type = models.CharField(max_length=20, choices=AUTH_TYPE_CHOICES, default='password', verbose_name='认证类型')
    username = models.CharField(max_length=100, verbose_name='用户名')
    password = models.CharField(max_length=255, blank=True, null=True, verbose_name='密码')
    private_key = models.TextField(blank=True, null=True, verbose_name='私钥')
    passphrase = models.CharField(max_length=255, blank=True, null=True, verbose_name='密钥口令')
    hosts = models.ManyToManyField(Host, blank=True, related_name='credentials', verbose_name='关联主机')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'SSH凭证'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} ({self.username})'
