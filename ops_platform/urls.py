"""
URL configuration for ops_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import index  # 导入首页视图

# Swagger文档配置
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="运维平台 API",
        default_version='v1',
        description="运维平台API文档",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', index, name='index'),  # 首页/仪表盘
    path('admin/', admin.site.urls),
    
    # 页面路由
    path('hosts/', include('hosts.urls', namespace='hosts')),  # 主机管理模块
    path('commands/', include('commands.urls', namespace='commands')),  # 命令执行模块
    
    # API接口
    path('api/v1/', include([
        path('', include('users.urls')),  # 用户模块
        path('navigation/', include('navigation.urls')),  # 导航系统模块
        path('commands/', include('commands.urls')),  # 批量命令执行模块
        path('hosts/', include('hosts.urls')),  # 主机管理模块
        # 其他模块的URL配置将在后续添加
    ])),
    
    # Swagger文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 修复静态文件URL配置
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
