from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserLoginLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    用户管理
    """
    list_display = ('id', 'username', 'email', 'phone', 'department', 'position', 'user_type', 'is_active', 'date_joined')
    list_filter = ('is_active', 'user_type', 'department')
    search_fields = ('username', 'email', 'phone', 'department')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('email', 'phone', 'department', 'position', 'avatar')}),
        (_('权限信息'), {'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'phone', 'department', 'position', 'user_type'),
        }),
    )


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    """
    用户登录日志管理
    """
    list_display = ('id', 'user', 'login_time', 'login_ip', 'login_type', 'is_success')
    list_filter = ('login_time', 'login_type', 'is_success')
    search_fields = ('user__username', 'login_ip')
    readonly_fields = ('user', 'login_time', 'login_ip', 'login_type', 'user_agent', 'is_success')
