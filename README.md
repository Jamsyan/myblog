

# MyBlog

一个基于微服务架构的现代化博客系统，采用前后端分离设计，支持多主题切换和灵活的权限管理。

## ✨ 核心特性

- **微服务架构**：基于 LinkGateway 网关的服务注册与发现机制
- **多引擎支持**：内置文件引擎(FileEngine)和权限引擎(PermDog)
- **主题系统**：支持中国红、丹青蓝、粉霞紫三种主题
- **权限管理**：基于 permission_level 的细粒度访问控制
- **插件机制**：支持性能监控、流量监控等插件扩展
- **现代化前端**：Vue 3 + Vite 构建，支持动画效果和响应式设计

## 🏗️ 系统架构

```
myblog/
├── my_blog_backend/          # 后端服务
│   ├── LinkGateway/          # 核心网关模块
│   │   ├── gateway.py        # 网关主入口
│   │   ├── registry.py       # 服务注册发现
│   │   ├── api_mapper.py     # API路由映射
│   │   ├── auth.py           # 认证授权
│   │   ├── db_link.py        # 数据库连接管理
│   │   └── plugin.py         # 插件系统
│   ├── engines/              # 业务引擎
│   │   ├── FileEngine/       # 文件处理引擎
│   │   └── PermDog/          # 权限管理引擎
│   ├── services/             # 业务服务
│   │   ├── post-service/     # 文章服务
│   │   ├── interaction-service/ # 互动服务(点赞/评论)
│   │   └── user-server/      # 用户服务
│   └── plugins/              # 插件实现
├── my_blog_frontend/         # 前端应用
│   └── src/
│       ├── modules/          # 业务模块
│       ├── components/       # 公共组件
│       └── styles/           # 样式文件
└── docker/                   # Docker配置
```

## 🚀 快速开始

### 环境要求

- Python 3.13+
- Node.js 20+
- SQLite (默认) 或其他数据库

### 后端启动

```bash
cd my_blog_backend
pip install -e .
python main.py
```

服务将在 `http://localhost:8000` 启动

### 前端启动

```bash
cd my_blog_frontend
npm install
npm run dev
```

服务将在 `http://localhost:5173` 启动

### Docker 部署

```bash
cd docker && docker-compose up -d
```

## 📖 文档导航

- [项目概述](./Docs/README.md#项目概述)
- [架构设计](./Docs/README.md#架构设计)
- [后端开发指南](./Docs/README.md#后端开发)
- [前端开发指南](./Docs/README.md#前端开发)
- [API文档](./Docs/README.md#API文档)
- [贡献指南](./Docs/CONTRIBUTING.md)

## 🔧 开发指南

### 项目结构规范

```
后端结构:
- engines/       # 引擎模块，每个引擎需包含 file_engine.json 配置
- services/      # 业务服务，每个服务需包含 service.json 配置
- plugins/       # 插件实现，需继承 Plugin 基类

前端结构:
- modules/       # 功能模块，包含视图、服务、状态管理
- components/    # 公共组件
- utils/         # 工具函数
```

### 核心模块说明

**LinkGateway**: 系统核心网关，负责服务注册发现、API路由映射、认证授权

**FileEngine**: 文章文件处理引擎，支持文章CRUD和评论管理

**PermDog**: 权限管理引擎，管理 permission_level (P0-P3) 和操作权限

### 添加新服务

1. 在 `services/` 目录创建服务文件夹
2. 添加 `service.json` 配置文件
3. 实现服务主类继承基础接口
4. 在网关中注册服务

### 添加新引擎

1. 在 `engines/` 目录创建引擎文件夹
2. 添加 `engine.json` 配置文件
3. 继承 `BaseEngine` 实现核心方法
4. 注册到服务注册中心

## 🎨 主题系统

系统内置三种主题，通过 CSS 类名切换:

| 主题 | 类名 | 描述 |
|------|------|------|
| 中国红 | `theme-china-red` | 传统红色系 |
| 丹青蓝 | `theme-danqing-blue` | 清新蓝色系 |
| 粉霞紫 | `theme-fenxia-purple` | 柔和紫色系 |

## 🔐 权限级别

| 级别 | 说明 | 访问范围 |
|------|------|----------|
| P0 | 公开 | 所有用户 |
| P1 | 内部 | 注册用户 |
| P2 | 私密 | 指定用户 |
| P3 | 私密 | 仅作者 |

## 🧪 测试

```bash
# 后端测试
cd my_blog_backend
pytest tests/

# 前端测试
cd my_blog_frontend
npm run test
```

## 📦 技术栈

**后端**:
- FastAPI / Uvicorn
- Pydantic
- SQLAlchemy
- Alembic

**前端**:
- Vue 3
- Vite
- Pinia
- Vue Router

**基础设施**:
- SQLite / PostgreSQL
- Docker
- GitHub Actions

## 🤝 贡献指南

欢迎贡献代码！请阅读 [贡献指南](./Docs/CONTRIBUTING.md) 了解:

- Fork 项目流程
- 代码规范要求
- Pull Request 要求
- 代码审查清单

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 获取帮助

- 查阅 [文档](./Docs/README.md)
- 查看 [常见问题](./Docs/README.md#常见问题)
- 通过 Issues 提问

---

MyBlog - 让分享更简单 ✨