from django.apps import AppConfig


class CommandsConfig(AppConfig):
    """命令执行应用配置"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'commands'
    verbose_name = '批量命令执行'
    
    def ready(self):
        """应用程序准备就绪时执行"""
        # 导入信号处理器
        import commands.signals
