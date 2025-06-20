from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from .models import Project, ProjectMember
from .serializers import ProjectSerializer, ProjectDetailSerializer, ProjectMemberSerializer
from core.response import APIResponse
from core.permissions import IsProjectOwner
from django.db.models import Q


class ProjectViewSet(viewsets.ModelViewSet):
    """
    项目管理视图
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_fields = ['name', 'key', 'owner']
    search_fields = ['name', 'key', 'description']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsProjectOwner()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer
    
    def get_queryset(self):
        user = self.request.user
        # 超级管理员可以看到所有项目
        if user.is_superuser:
            return Project.objects.all()
        
        # 普通用户只能看到自己创建的、负责的或参与的项目
        return Project.objects.filter(
            Q(owner=user) | Q(created_by=user) | Q(members__user=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """
        添加项目成员
        """
        project = self.get_object()
        serializer = ProjectMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 检查用户是否已经是项目成员
        user_id = serializer.validated_data.get('user').id
        if ProjectMember.objects.filter(project=project, user_id=user_id).exists():
            return APIResponse(code=400, message='该用户已经是项目成员', status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(project=project)
        return APIResponse(data=serializer.data, message='成员添加成功')
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """
        移除项目成员
        """
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return APIResponse(code=400, message='请提供用户ID', status=status.HTTP_400_BAD_REQUEST)
            
        try:
            member = ProjectMember.objects.get(project=project, user_id=user_id)
            member.delete()
            return APIResponse(message='成员移除成功')
        except ProjectMember.DoesNotExist:
            return APIResponse(code=404, message='该用户不是项目成员', status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        获取项目成员列表
        """
        project = self.get_object()
        members = ProjectMember.objects.filter(project=project)
        serializer = ProjectMemberSerializer(members, many=True)
        return APIResponse(data=serializer.data)
    
    @action(detail=True, methods=['put'])
    def update_member_role(self, request, pk=None):
        """
        更新项目成员角色
        """
        project = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        
        if not user_id or not role:
            return APIResponse(code=400, message='请提供用户ID和角色', status=status.HTTP_400_BAD_REQUEST)
            
        try:
            member = ProjectMember.objects.get(project=project, user_id=user_id)
            member.role = role
            member.save(update_fields=['role'])
            return APIResponse(message='成员角色更新成功')
        except ProjectMember.DoesNotExist:
            return APIResponse(code=404, message='该用户不是项目成员', status=status.HTTP_404_NOT_FOUND) 