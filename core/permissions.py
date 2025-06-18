from rest_framework.permissions import BasePermission
import json

class IsAdminUser(BasePermission):
    """
    限制只有管理员用户才能访问
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff))

class RoleBasedPermission(BasePermission):
    """
    基于角色的权限控制类
    """
    def __init__(self, required_permission):
        self.required_permission = required_permission
        
    def has_permission(self, request, view):
        # 超级管理员拥有所有权限
        if request.user.is_superuser:
            return True
        
        # 检查用户角色权限
        if not hasattr(request.user, 'role'):
            return False
            
        user_role = request.user.role
        if not user_role:
            return False
            
        # 获取角色权限
        permissions = {}
        if user_role.permissions:
            try:
                permissions = json.loads(user_role.permissions)
            except (json.JSONDecodeError, TypeError):
                return False
                
        # 检查权限
        return permissions.get(self.required_permission, False)


class IsProjectOwner(BasePermission):
    """
    项目所有者权限
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class HasBuildAccess(BasePermission):
    """
    构建任务权限
    """
    def has_object_permission(self, request, view, obj):
        # 项目所有者有权限
        if obj.project.owner == request.user:
            return True
            
        # 任务创建者有权限
        if obj.created_by == request.user:
            return True
            
        # 基于角色检查
        return RoleBasedPermission('build_access').has_permission(request, view) 