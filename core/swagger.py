from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# 创建无需认证的schema_view
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
   authentication_classes=(),
) 