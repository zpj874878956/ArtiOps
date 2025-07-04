from django.apps import AppConfig


class HostsConfig(AppConfig):
    """主机管理应用配置"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hosts'
    verbose_name = '主机管理'
