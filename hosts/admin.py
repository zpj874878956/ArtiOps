from django.contrib import admin
from .models import Host, HostGroup, HostTag, SSHCredential


@admin.register(HostGroup)
class HostGroupAdmin(admin.ModelAdmin):
    """主机组管理"""
    list_display = ('name', 'description', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    """主机管理"""
    list_display = ('hostname', 'ip_address', 'port', 'os_type', 'status', 'created_by', 'created_at')
    search_fields = ('hostname', 'ip_address', 'description')
    list_filter = ('status', 'os_type', 'created_at', 'groups')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('groups',)
    fieldsets = (
        ('基本信息', {
            'fields': ('hostname', 'ip_address', 'port', 'status', 'description')
        }),
        ('系统信息', {
            'fields': ('os_type', 'os_version')
        }),
        ('分组信息', {
            'fields': ('groups',)
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(HostTag)
class HostTagAdmin(admin.ModelAdmin):
    """主机标签管理"""
    list_display = ('name', 'color', 'created_by', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    filter_horizontal = ('hosts',)
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'color')
        }),
        ('关联主机', {
            'fields': ('hosts',)
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at')
        }),
    )


@admin.register(SSHCredential)
class SSHCredentialAdmin(admin.ModelAdmin):
    """SSH凭证管理"""
    list_display = ('name', 'auth_type', 'username', 'is_default', 'created_by', 'created_at')
    search_fields = ('name', 'username')
    list_filter = ('auth_type', 'is_default', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('hosts',)
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'auth_type', 'is_default')
        }),
        ('认证信息', {
            'fields': ('username', 'password', 'private_key', 'passphrase')
        }),
        ('关联主机', {
            'fields': ('hosts',)
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
