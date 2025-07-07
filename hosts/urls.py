from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import HostViewSet, HostGroupViewSet, HostTagViewSet, SSHCredentialViewSet
from .page_views import (
    host_list,
    host_group_list,
    host_tag_list,
    ssh_credential_list,
    host_detail,
    test_ssh_connection
)
from .api_views import get_ssh_credentials, get_credential_detail, delete_credential

# 设置应用名称
app_name = 'hosts'

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'api/hosts', HostViewSet)
router.register(r'api/groups', HostGroupViewSet)
router.register(r'api/tags', HostTagViewSet)
router.register(r'api/credentials', SSHCredentialViewSet)

# URL配置
urlpatterns = [
    # API接口
    path('api/', include(router.urls)),
    
    # 页面视图
    path('', host_list, name='host_list'),
    path('groups/', host_group_list, name='host_group_list'),
    path('tags/', host_tag_list, name='host_tag_list'),
    path('credentials/', ssh_credential_list, name='ssh_credential_list'),
    path('detail/<int:host_id>/', host_detail, name='host_detail'),
    
    # AJAX接口
    path('test-ssh/', test_ssh_connection, name='test_ssh_connection'),
    path('api/credentials/list/', get_ssh_credentials, name='get_ssh_credentials'),
    path('api/credentials/<int:credential_id>/', get_credential_detail, name='get_credential_detail'),
    path('api/credentials/<int:credential_id>/delete/', delete_credential, name='delete_credential'),
]