from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('用户管理')
    
    def ready(self):
        """
        应用启动时执行的初始化操作
        """
        # 导入信号处理器
        import users.signals  # noqa
