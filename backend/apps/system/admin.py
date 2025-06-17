from django.contrib import admin
from .models import SystemConfig

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_encrypted', 'description', 'updated_at')
    list_filter = ('is_encrypted',)
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at') 