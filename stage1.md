# 阶段一运维平台需求文档

## 1. 项目概述
本项目是基于Django (Python后端) 和 Vue 3 (TypeScript前端) 的轻量级运维管理平台，聚焦核心运维管理功能，为后续功能扩展奠定基础。

**核心功能模块**:
- 项目管理：项目基本信息管理
- 构建与部署：构建任务管理与历史
- 日志与监控：用户操作审计
- 用户与权限：用户角色管理系统
- 凭据管理：敏感信息安全管理
- 环境配置：多环境管理
- 系统配置：平台基础设置

## 2. 功能详细说明

### 2.1 项目管理
#### 项目列表
- 项目信息展示表格
- 字段：项目ID、项目名称、项目标识、负责人、创建时间、最后更新时间
- 操作：创建项目、编辑项目、删除项目、项目搜索
- 详情页：展示项目关联的环境和构建任务

### 2.2 构建与部署
#### 构建任务
- 创建构建任务表单
  - 任务名称、关联项目、构建命令、构建参数
  - 环境变量配置
  - 执行账户选择
- 任务状态管理：创建、启动、暂停、终止
- 任务调度：立即执行或定时执行
- 实时日志输出展示

#### 构建历史
- 按任务展示构建历史记录
- 历史记录信息：执行时间、持续时间、执行状态(成功/失败)、操作人
- 构建详情：查看完整日志输出、下载构建产物
- 重新执行和结果分析功能

### 2.3 日志与监控
#### 登录日志
- 登录记录表格展示
- 字段：用户名、登录IP、登录时间、登录状态（成功/失败）、登录方式
- 筛选功能：按时间范围、用户名、登录状态筛选
- 导出日志功能（CSV格式）

### 2.4 用户与权限
#### 用户管理
- 用户列表：用户名、姓名、邮箱、角色、状态（启用/禁用）
- 用户操作：新增用户、编辑用户、删除用户、重置密码
- 用户状态切换（启用/禁用）

#### 角色管理
- 角色列表：角色名称、角色标识、描述
- 权限分配：细粒度权限控制（项目查看/编辑、任务执行/管理等）
- 角色关联：为用户分配角色
- 角色复制功能（基于现有角色创建新角色）

### 2.5 凭据管理
- 凭据类型管理：SSH密钥、API密钥、用户名密码等
- 凭据安全存储（AES加密）
- 凭据使用记录审计
- 凭据轮换策略设置
- 凭据关联：关联到具体项目或任务

### 2.6 环境配置
#### 环境列表
- 环境分类：开发、测试、预生产、生产环境
- 环境参数：环境名称、标识、描述、API端点
- 环境关联：为项目绑定环境
- 环境变量管理：全局环境变量和项目级变量

### 2.7 系统配置
#### 基本配置
- 系统信息：平台名称、Logo设置
- 安全设置：登录失败锁定策略、会话超时时间
- 通知配置：SMTP邮件服务设置
- 系统维护状态切换
- API访问密钥管理

## 3. 系统架构设计

### 3.1 技术架构
![29800e63e235673d.png](http://pic.zzppjj.top/LightPicture/2025/06/29800e63e235673d.png)

### 3.2 构建任务处理流程
![bc42eb766495a608.png](http://pic.zzppjj.top/LightPicture/2025/06/bc42eb766495a608.png)

## 4. 数据库设计（核心表）

### 4.1 核心表结构
![2949f740b0f98a80.png](http://pic.zzppjj.top/LightPicture/2025/06/2949f740b0f98a80.png)

### 4.2 关键表字段
**users 用户表**
- id, username, password, real_name, email, status(active/inactive), role_id, created_at

**roles 角色表**
- id, name, permissions(json), description, created_at

**projects 项目表**
- id, name, key(唯一标识), description, owner_id, created_at

**environments 环境表**
- id, name, type(dev/test/staging/prod), project_id, variables(json)

**build_tasks 构建任务表**
- id, name, project_id, command, parameters, credential_id, status, created_by

## 5. API 设计规范

### 5.1 统一响应格式
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "name": "示例项目"
  },
  "timestamp": 1690000000
}
```

### 5.2 主要API端点
| 模块 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 用户 | GET | /api/v1/users | 获取用户列表 |
| 用户 | POST | /api/v1/users | 创建新用户 |
| 项目 | GET | /api/v1/projects | 获取项目列表 |
| 项目 | POST | /api/v1/projects | 创建新项目 |
| 构建任务 | POST | /api/v1/build/tasks/{id}/run | 执行构建任务 |
| 构建历史 | GET | /api/v1/build/history | 获取构建历史 |
| 凭据 | POST | /api/v1/credentials | 创建新凭据 |
| 登录日志 | GET | /api/v1/logs/login | 获取登录日志 |

## 6. 安全设计

### 6.1 认证与授权
- JWT(JSON Web Token)认证
- 基于角色的访问控制(RBAC)
- 细粒度权限管理(每个API端点做权限校验)
- 敏感操作审计(创建、删除、权限变更等)

### 6.2 数据安全
- 用户密码：bcrypt加密存储
- 凭据数据：AES-256加密存储
- HTTPS传输所有数据
- SQL注入防护（ORM自动处理）
- XSS攻击防护（前端自动转义）

## 7. 开发与部署

### 7.1 开发环境
```yaml
后端:
  Python: 3.10+
  Django: 4.x
  MySQL: 5.7
  Redis: 5.x
  Celery: 5.x

前端:
  Node.js: 16.x+
  Vue: 3.x
  TypeScript: 4.x
  Element Plus: 2.x
```

### 7.2 部署方案
![1f4e891ba80afc1f.png](http://pic.zzppjj.top/LightPicture/2025/06/1f4e891ba80afc1f.png)

## 8. 扩展性设计

### 8.1 代码结构
```
backend/
  ├── apps/
  │   ├── users/       # 用户模块
  │   ├── projects/    # 项目模块
  │   ├── builds/      # 构建模块
  │   └── system/      # 系统模块
  ├── core/            # 核心组件
  └── config/          # 配置文件

frontend/
  ├── src/
  │   ├── views/
  │   │   ├── Project/  # 项目视图
  │   │   ├── Build/    # 构建视图
  │   │   └── System/   # 系统视图
  │   ├── services/     # API服务
  │   └── store/        # 状态管理
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwMjU4NjEzLCJpYXQiOjE3NTAyNTUwMTMsImp0aSI6Ijg4YTZlZmU1OTVmMjQzNzBiNGUwNDMzNzBlNzQ2MjZjIiwidXNlcl9pZCI6MX0.07ae-ryfpx98DOWvfeJexQuVgdhLMSkqja1fExTwVa8

cryptography