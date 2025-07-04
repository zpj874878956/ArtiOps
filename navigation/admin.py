from django.contrib import admin
from .models import SystemCategory, ExternalSystem, SystemPermission, UserFavorite, AccessLog


@admin.register(SystemCategory)
class SystemCategoryAdmin(admin.ModelAdmin):
    """
    系统分类管理
    """
    list_display = ('name', 'order', 'created_at', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExternalSystem)
class ExternalSystemAdmin(admin.ModelAdmin):
    """
    外部系统管理
    """
    list_display = ('name', 'system_type', 'category', 'base_url', 'status', 'is_active', 'access_count', 'score')
    list_filter = ('system_type', 'category', 'status', 'is_active')
    search_fields = ('name', 'description', 'base_url')
    ordering = ('-score', 'order', 'name')
    readonly_fields = ('access_count', 'score', 'created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'system_type', 'category', 'description', 'icon', 'order')
        }),
        ('访问配置', {
            'fields': ('base_url', 'api_base_url', 'status', 'is_active')
        }),
        ('统计信息', {
            'fields': ('access_count', 'score')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )


@admin.register(SystemPermission)
class SystemPermissionAdmin(admin.ModelAdmin):
    """
    系统权限管理
    """
    list_display = ('system', 'user', 'group', 'can_access', 'created_at')
    list_filter = ('can_access', 'system')
    search_fields = ('system__name', 'user__username', 'group__name')
    ordering = ('system', 'user', 'group')
    readonly_fields = ('created_at',)


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    """
    用户收藏管理
    """
    list_display = ('user', 'system', 'created_at')
    list_filter = ('user', 'system')
    search_fields = ('user__username', 'system__name')
    ordering = ('user', 'system')
    readonly_fields = ('created_at',)


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    """
    访问日志管理
    """
    list_display = ('user', 'system', 'access_time', 'access_ip')
    list_filter = ('user', 'system', 'access_time')
    search_fields = ('user__username', 'system__name', 'access_ip')
    ordering = ('-access_time',)
    readonly_fields = ('user', 'system', 'access_time', 'access_ip', 'user_agent')
    fieldsets = (
        ('访问信息', {
            'fields': ('user', 'system', 'access_time')
        }),
        ('客户端信息', {
            'fields': ('access_ip', 'user_agent')
        }),
    )
