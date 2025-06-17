"""
初始化系统配置的管理命令
"""
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.system.models import SystemConfig
from django.utils.translation import gettext_lazy as _
from core.encryption import AESCipher

DEFAULT_CONFIGS = [
    {
        "key": "site_name",
        "value": "ArtiOps - AI驱动的DevOps自动化平台",
        "description": "站点名称",
        "is_encrypted": False
    },
    {
        "key": "site_description",
        "value": "基于人工智能的DevOps自动化平台，提供项目管理、CI/CD、环境管理等功能",
        "description": "站点描述",
        "is_encrypted": False
    },
    {
        "key": "admin_email",
        "value": "admin@example.com",
        "description": "管理员邮箱",
        "is_encrypted": False
    },
    {
        "key": "smtp_server",
        "value": "smtp.example.com",
        "description": "SMTP服务器地址",
        "is_encrypted": False
    },
    {
        "key": "smtp_port",
        "value": "587",
        "description": "SMTP服务器端口",
        "is_encrypted": False
    },
    {
        "key": "smtp_username",
        "value": "user@example.com",
        "description": "SMTP用户名",
        "is_encrypted": False
    },
    {
        "key": "smtp_password",
        "value": "password",
        "description": "SMTP密码",
        "is_encrypted": True
    },
    {
        "key": "smtp_use_tls",
        "value": "True",
        "description": "SMTP是否使用TLS",
        "is_encrypted": False
    },
    {
        "key": "max_build_time",
        "value": "3600",
        "description": "最大构建时间（秒）",
        "is_encrypted": False
    },
    {
        "key": "default_build_timeout",
        "value": "1800",
        "description": "默认构建超时时间（秒）",
        "is_encrypted": False
    },
    {
        "key": "log_retention_days",
        "value": "30",
        "description": "日志保留天数",
        "is_encrypted": False
    },
    {
        "key": "allowed_file_extensions",
        "value": "jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx,zip,tar,gz",
        "description": "允许上传的文件扩展名",
        "is_encrypted": False
    },
    {
        "key": "max_file_size",
        "value": "10485760",  # 10MB in bytes
        "description": "最大文件大小（字节）",
        "is_encrypted": False
    },
    {
        "key": "enable_registration",
        "value": "True",
        "description": "是否允许新用户注册",
        "is_encrypted": False
    },
    {
        "key": "enable_api_throttling",
        "value": "True",
        "description": "是否启用API限流",
        "is_encrypted": False
    },
    {
        "key": "api_throttle_rate",
        "value": "100/hour",
        "description": "API限流速率",
        "is_encrypted": False
    }
]

class Command(BaseCommand):
    help = _('初始化系统配置')

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help=_('强制更新已存在的配置'),
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # 初始化系统配置
        self.stdout.write(self.style.HTTP_INFO(_('开始初始化系统配置...')))
        
        aes_cipher = AESCipher(settings.ENCRYPTION_KEY)
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for config in DEFAULT_CONFIGS:
            key = config['key']
            value = config['value']
            is_encrypted = config['is_encrypted']
            description = config['description']
            
            # 如果是加密字段，对值进行加密
            if is_encrypted:
                value = aes_cipher.encrypt(value)
            
            # 检查配置是否已存在
            config_obj, created = SystemConfig.objects.get_or_create(
                key=key,
                defaults={
                    'value': value,
                    'description': description,
                    'is_encrypted': is_encrypted
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(_('创建配置: {}').format(key)))
            else:
                # 如果配置已存在且设置了force选项，则更新配置
                if force:
                    config_obj.value = value
                    config_obj.description = description
                    config_obj.is_encrypted = is_encrypted
                    config_obj.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(_('更新配置: {}').format(key)))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.NOTICE(_('跳过已存在的配置: {}').format(key)))
        
        # 输出统计信息
        self.stdout.write(self.style.SUCCESS(_('系统配置初始化完成!')))
        self.stdout.write(self.style.HTTP_INFO(_('创建: {}, 更新: {}, 跳过: {}').format(
            created_count, updated_count, skipped_count
        ))) 