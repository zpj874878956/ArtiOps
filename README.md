# 运维平台

基于Django的运维平台，提供用户管理、主机管理、批量命令执行和系统导航等功能。

## 功能特性

- 用户管理：用户注册、登录、权限控制
- 主机管理：主机信息管理、标签分组
- 批量命令执行：支持Ansible和Shell模式
- 系统导航：快速访问常用系统

## 技术栈

- 后端：Django 4.2, Django REST Framework
- 数据库：MySQL
- 认证：JWT, OAuth2
- 文档：Swagger/OpenAPI

## 安装说明

### 环境要求

- Python 3.8+
- MySQL 5.7+

### 安装步骤

1. 克隆代码库

```bash
git clone https://github.com/yourusername/ops_platform.git
cd ops_platform
```

2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 配置数据库

```bash
# 修改settings.py中的数据库配置
```

5. 执行数据库迁移

```bash
python manage.py migrate
```

6. 创建超级用户

```bash
python manage.py createsuperuser
```

7. 启动开发服务器

```bash
python manage.py runserver
```

## 使用指南

- 访问管理后台：http://localhost:8000/admin/
- API文档：http://localhost:8000/swagger/
- API接口：http://localhost:8000/api/v1/

## 开发指南

### 项目结构

```
ops_platform/
├── core/          # 公共模块
├── users/         # 用户模块
├── hosts/         # 主机管理模块
├── commands/      # 命令执行模块
└── navigation/    # 系统导航模块
```

### 开发流程

1. 创建新功能分支
2. 编写代码和测试
3. 提交代码并创建合并请求
4. 代码审查和合并

## 贡献指南

欢迎贡献代码，请遵循以下步骤：

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 推送到分支
5. 创建合并请求

## 许可证

[MIT](LICENSE)