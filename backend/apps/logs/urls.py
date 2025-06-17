from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginLogViewSet, OperationLogViewSet

router = DefaultRouter()
router.register('login', LoginLogViewSet)
router.register('operation', OperationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 