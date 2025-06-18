from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('roles', RoleViewSet)

# 添加直接的登录路径
login_view = UserViewSet.as_view({'post': 'login'})

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='user-login'),  # 显式添加登录路径
] 