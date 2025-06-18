from django.contrib import admin
from .models import Environment

@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'project', 'created_by', 'created_at')
    list_filter = ('type', 'project')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at') 