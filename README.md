# ArtiOps后端

ArtiOps是一个基于Django REST framework的API后端系统，用于管理CI/CD流程。

## 项目结构指南

为了帮助开发者更好地理解项目结构，以下是主要目录和文件的功能说明：

```
backend/
├── apps/                   # 应用目录，包含所有业务模块
│   ├── users/              # 用户管理模块
│   │   ├── models.py       # 数据模型定义
│   │   ├── serializers.py  # 序列化器定义
│   │   ├── views.py        # 视图定义
│   │   └── urls.py         # URL路由配置
│   ├── projects/           # 项目管理模块
│   ├── builds/             # 构建管理模块
│   └── ...                 # 其他业务模块
├── config/                 # 项目配置
│   ├── settings.py         # Django设置
│   ├── urls.py             # 主URL路由
│   └── wsgi.py             # WSGI配置
├── core/                   # 核心功能模块
│   ├── response.py         # API响应处理
│   ├── permissions.py      # 权限控制
│   └── exceptions.py       # 异常处理
├── manage.py               # Django命令行工具
└── requirements.txt        # 项目依赖
```

## 开发模式

ArtiOps 采用标准的Django REST framework开发模式，主要包括：

1. **模型层(Model)**：在`models.py`中定义数据结构
2. **序列化层(Serializer)**：在`serializers.py`中定义数据转换和验证规则
3. **视图层(View)**：在`views.py`中定义业务逻辑和API端点
4. **URL配置**：在`urls.py`中定义API路由

这种结构使代码保持清晰的职责分离，提高可维护性和可扩展性。

## 开始使用

1. 创建虚拟环境：
```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖：
```
pip install -r requirements.txt
```

3. 配置环境变量：
```
cp .env.example .env
# 编辑.env文件设置数据库等配置
```

4. 运行开发服务器：
```
python manage.py runserver
```

## 开发新功能

按照以下步骤开发新功能：

1. 在models.py中定义数据模型
2. 在serializers.py中定义序列化器
3. 在views.py中定义视图
4. 在urls.py中配置URL路由
5. 在config/urls.py中注册应用的URL

## 代码示例

以下是一个典型的Django REST framework开发流程示例：

### models.py - 定义模型
```python
from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### serializers.py - 定义序列化器
```python
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
```

### views.py - 定义视图
```python
from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
```

### urls.py - 配置URL
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register('tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

这种结构使得代码逻辑清晰，易于理解和维护。

## 项目说明

ArtiOps是一个AI驱动的DevOps自动化平台，后端使用Django REST framework构建。

## 技术栈

- Python 3.8+
- Django 4.2.0
- Django REST Framework 3.14.0
- JWT认证
- MySQL/SQLite数据库
- Celery任务队列
- Redis缓存

## 项目结构

```
backend/
├── apps/               # 应用模块
│   ├── builds/         # 构建管理
│   ├── credentials/    # 凭证管理
│   ├── environments/   # 环境管理
│   ├── logs/           # 日志管理
│   ├── projects/       # 项目管理
│   ├── system/         # 系统管理
│   └── users/          # 用户管理
├── config/             # 项目配置
│   ├── settings.py     # 项目设置
│   ├── urls.py         # URL路由
│   └── ...
├── core/               # 核心功能
├── docs/               # 文档
├── logs/               # 日志文件
├── manage.py           # Django管理脚本
├── requirements.txt    # 项目依赖
└── start.py            # 启动脚本
```

## 纯API后端说明

本项目是一个纯API后端，不包含任何前端代码。所有前端相关的内容已被移除：

1. 移除了Django管理界面相关配置
2. 移除了前端开发服务器启动功能
3. 保留了最小化的静态文件配置，仅用于API文档(Swagger/ReDoc)
4. 设置了CORS，允许独立的前端应用访问API

## 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
#激活虚拟环境
cd backend
.\venv\Scripts\activate
python start.py

# 或者使用Django命令
#激活虚拟环境
cd backend
.\venv\Scripts\activate
python manage.py runserver
```

## API文档

启动服务后，可以通过以下URL访问API文档：

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## 环境变量

项目使用.env文件或环境变量进行配置，主要环境变量包括：

- SECRET_KEY: Django密钥
- DEBUG: 调试模式(True/False)
- ALLOWED_HOSTS: 允许的主机
- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT: 数据库配置
- CORS_ALLOWED_ORIGINS: 允许跨域请求的源
- CELERY_BROKER_URL, CELERY_RESULT_BACKEND: Celery配置
- ENCRYPTION_KEY: 加密密钥 

# 管理员用户创建成功，用户名: admin，密码: Admin@2023