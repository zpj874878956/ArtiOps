# ArtiOps开发者指南

这个指南帮助您理解ArtiOps项目的结构和开发流程。

## Django基础概念

Django是一个高级Python Web框架，采用MVT（Model-View-Template）模式：

- **Model（模型）**：定义数据结构，对应数据库表
- **View（视图）**：处理业务逻辑
- **Template（模板）**：负责HTML渲染（在REST API中通常不直接使用）

在Django REST framework中，还有一个重要概念：

- **Serializer（序列化器）**：负责数据转换和验证，类似于表单验证

## 项目结构

ArtiOps采用标准的Django REST framework项目结构：

```
app/
  ├── models.py      # 数据模型
  ├── serializers.py # 序列化器
  ├── views.py       # 视图
  └── urls.py        # URL路由
```

## 开发流程示例

下面是一个完整的开发流程示例，展示如何创建一个新功能：

### 1. 定义模型（models.py）

```python
from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name="项目名称")
    description = models.TextField(blank=True, verbose_name="项目描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "项目"
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.name
```

### 2. 定义序列化器（serializers.py）

```python
from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']
```

### 3. 定义视图（views.py）

```python
from rest_framework import viewsets
from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filterset_fields = ['name']
    search_fields = ['name', 'description']
```

### 4. 配置URL路由（urls.py）

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

router = DefaultRouter()
router.register('projects', ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

### 5. 在主URL配置中注册应用

在`config/urls.py`中添加：

```python
urlpatterns = [
    # ... 其他URL配置
    path('api/projects/', include('apps.projects.urls')),
]
```

## API交互流程

当客户端发送请求时，Django REST framework的处理流程：

1. 请求到达URL路由
2. 路由将请求分发到对应的视图
3. 视图使用序列化器验证和转换数据
4. 视图处理业务逻辑并返回响应

## 常见任务示例

### 创建自定义API端点

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class ProjectViewSet(viewsets.ModelViewSet):
    # ... 其他代码
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        project = self.get_object()
        project.is_archived = True
        project.save()
        return Response({'status': 'project archived'})
```

### 添加权限控制

```python
from rest_framework import permissions

class ProjectViewSet(viewsets.ModelViewSet):
    # ... 其他代码
    permission_classes = [permissions.IsAuthenticated]
```

## 调试技巧

1. 使用`print`语句或Python的`logging`模块输出调试信息
2. 在Django shell中测试代码：`python manage.py shell`
3. 查看Django的调试页面，了解错误详情

## 进阶学习资源

- [Django官方文档](https://docs.djangoproject.com/)
- [Django REST framework文档](https://www.django-rest-framework.org/)
- [Django Girls教程](https://tutorial.djangogirls.org/)

希望这个指南能帮助您更好地理解和开发ArtiOps项目！
