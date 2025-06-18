from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SystemConfigViewSet

router = DefaultRouter()
router.register('config', SystemConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 