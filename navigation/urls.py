from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SystemCategoryViewSet, ExternalSystemViewSet, 
    SystemPermissionViewSet, UserFavoriteViewSet, AccessLogViewSet
)

router = DefaultRouter()
router.register(r'categories', SystemCategoryViewSet, basename='system-category')
router.register(r'systems', ExternalSystemViewSet, basename='external-system')
router.register(r'permissions', SystemPermissionViewSet, basename='system-permission')
router.register(r'favorites', UserFavoriteViewSet, basename='user-favorite')
router.register(r'access-logs', AccessLogViewSet, basename='access-log')

urlpatterns = [
    path('', include(router.urls)),
]