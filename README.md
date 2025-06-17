# ArtiOps - AI驱动的DevOps自动化平台

ArtiOps是一个基于人工智能的DevOps自动化平台，提供项目管理、CI/CD、环境管理等功能，旨在简化开发运维流程，提高团队协作效率。

## 功能特点

- **智能化项目管理**：基于AI的项目分析和优化建议
- **自动化构建与部署**：支持多种CI/CD流程
- **环境管理**：统一管理开发、测试、生产环境
- **凭证管理**：安全存储和管理各类访问凭证
- **系统配置**：灵活的系统配置管理
- **操作日志**：详细记录系统操作，支持审计追踪

## 系统架构

- **前端**：React + Ant Design + TypeScript
- **后端**：Django + Django REST Framework
- **数据库**：MySQL
- **缓存**：Redis
- **任务队列**：Celery

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+
- MySQL 5.7+
- Redis 5.0+

### 开发环境搭建

1. 克隆仓库

```bash
git clone https://github.com/yourusername/artiops.git
cd artiops
```

2. 后端设置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，设置必要的环境变量

# 初始化数据库
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 初始化系统配置
python manage.py init_system
```

3. 前端设置

```bash
cd frontend
npm install
```

4. 启动开发服务器

```bash
# 使用启动脚本
python start.py

# 或分别启动前后端
# 后端
python manage.py runserver

# 前端
cd frontend
npm start
```

## 使用说明

访问 http://localhost:3000 打开前端界面，使用超级用户账号登录管理后台。

## 项目结构

```
artiops/
├── backend/                # 后端代码
│   ├── apps/               # 应用模块
│   │   ├── builds/         # 构建管理
│   │   ├── credentials/    # 凭证管理
│   │   ├── environments/   # 环境管理
│   │   ├── logs/           # 日志管理
│   │   ├── projects/       # 项目管理
│   │   ├── system/         # 系统管理
│   │   └── users/          # 用户管理
│   ├── core/               # 核心功能
│   └── config/             # 项目配置
├── frontend/               # 前端代码
├── logs/                   # 日志文件
├── .env                    # 环境变量
├── manage.py               # Django管理脚本
├── requirements.txt        # Python依赖
├── start.py                # 启动脚本
└── README.md               # 项目说明
```

## 贡献指南

欢迎贡献代码，请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。
```
python start.py --backend-only
python start.py --skip-migrations --skip-checks