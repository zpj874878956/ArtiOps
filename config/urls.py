from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from core.swagger import schema_view  # 导入自定义schema_view
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# API路由
api_v1_patterns = [
    path('', include('apps.users.urls')),  # 用户应用路径修改为根路径，使登录接口更容易访问
    path('projects/', include('apps.projects.urls')),
    path('build/', include('apps.builds.urls')),
    path('system/', include('apps.system.urls')),
    path('credentials/', include('apps.credentials.urls')),
    path('environments/', include('apps.environments.urls')),
    path('logs/', include('apps.logs.urls')),
]

urlpatterns = [
    # Django管理界面
    path('admin/', admin.site.urls),
    
    # 纯API后端路由
    path('api/v1/', include(api_v1_patterns)),
    
    # API文档 - 仅用于开发和调试
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# 开发环境下的媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 