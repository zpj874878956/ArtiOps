from django.apps import AppConfig


class NavigationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'navigation'
    verbose_name = '导航系统'  # 应用的中文名称
    
    def ready(self):
        """
        在应用完全加载后导入信号处理模块
        这样可以避免循环导入问题
        """
        # 导入信号处理模块，确保信号被注册
        import navigation.signals
