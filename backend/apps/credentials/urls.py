from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CredentialViewSet, CredentialUsageLogViewSet

router = DefaultRouter()
router.register('', CredentialViewSet)
router.register('logs', CredentialUsageLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 