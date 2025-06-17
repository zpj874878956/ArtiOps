from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet

router = DefaultRouter()
router.register('', UserViewSet)
router.register('roles', RoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 