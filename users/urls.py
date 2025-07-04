from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserLoginLogViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('login-logs', UserLoginLogViewSet, basename='login-log')

urlpatterns = [
    path('', include(router.urls)),
]