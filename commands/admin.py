from django.contrib import admin
from .models import CommandTemplate, CommandExecution, ExecutionLog, DangerousCommand


@admin.register(CommandTemplate)
class CommandTemplateAdmin(admin.ModelAdmin):
    """命令模板管理"""
    list_display = ('name', 'template_type', 'description', 'is_public', 'created_by', 'created_at', 'updated_at')
    list_filter = ('template_type', 'is_public', 'created_at')
    search_fields = ('name', 'description', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'template_type', 'description', 'is_public')
        }),
        ('命令内容', {
            'fields': ('content',)
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(CommandExecution)
class CommandExecutionAdmin(admin.ModelAdmin):
    """命令执行管理"""
    list_display = ('name', 'execution_type', 'status', 'created_by', 'start_time', 'end_time')
    list_filter = ('execution_type', 'status', 'start_time')
    search_fields = ('name', 'command_content', 'target_hosts')
    readonly_fields = ('start_time', 'end_time', 'result')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'execution_type', 'status')
        }),
        ('命令信息', {
            'fields': ('command_content', 'template', 'target_hosts', 'parameters')
        }),
        ('执行结果', {
            'fields': ('result', 'start_time', 'end_time')
        }),
        ('创建信息', {
            'fields': ('created_by',)
        }),
    )


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    """执行日志管理"""
    list_display = ('execution', 'host', 'log_level', 'message', 'timestamp')
    list_filter = ('log_level', 'timestamp', 'host')
    search_fields = ('message', 'host')
    readonly_fields = ('timestamp',)
    fieldsets = (
        ('日志信息', {
            'fields': ('execution', 'host', 'log_level', 'message', 'timestamp')
        }),
    )


@admin.register(DangerousCommand)
class DangerousCommandAdmin(admin.ModelAdmin):
    """危险命令管理"""
    list_display = ('pattern', 'command_type', 'description', 'action', 'created_by')
    list_filter = ('command_type', 'action')
    search_fields = ('pattern', 'description')
    fieldsets = (
        ('规则信息', {
            'fields': ('pattern', 'command_type', 'description', 'action')
        }),
        ('创建信息', {
            'fields': ('created_by',)
        }),
    )
