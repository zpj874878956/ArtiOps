from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API文档配置
schema_view = get_schema_view(
   openapi.Info(
      title="ArtiOps API",
      default_version='v1',
      description="ArtiOps运维平台API文档",
      terms_of_service="",
      contact=openapi.Contact(email="admin@example.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# API路由
api_v1_patterns = [
    path('users/', include('apps.users.urls')),
    path('projects/', include('apps.projects.urls')),
    path('build/', include('apps.builds.urls')),
    path('system/', include('apps.system.urls')),
    path('credentials/', include('apps.credentials.urls')),
    path('environments/', include('apps.environments.urls')),
    path('logs/', include('apps.logs.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
    
    # API文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# 开发环境下的媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 