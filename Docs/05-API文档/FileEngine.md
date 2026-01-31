# FileEngine 文档

## 1. 引擎简介

FileEngine是LinkGateway内置的文件处理引擎，提供了基本的帖子和评论管理功能。它采用文件存储方式，支持Markdown和HTML格式的帖子存储，以及冷热分离的评论管理策略。

## 2. 功能特性

### 2.1 帖子管理

- **帖子创建**：支持创建Markdown或HTML格式的帖子
- **帖子编辑**：支持更新帖子内容和标题
- **帖子删除**：支持删除帖子
- **帖子获取**：支持根据ID获取帖子

### 2.2 评论管理

- **评论添加**：支持为帖子添加评论
- **评论获取**：支持分页获取帖子的评论
- **冷热分离**：支持热门评论和冷评论的自动分类和存储

### 2.3 其他功能

- **健康检查**：支持引擎健康状态检查
- **元数据获取**：支持获取引擎元数据信息

## 3. 技术架构

### 3.1 核心组件

| 组件名称 | 功能描述 | 文件位置 |
|---------|---------|---------|
| FileEngine | 引擎主类，协调各个模块工作 | engines/FileEngine/file_engine.py |
| PostManager | 帖子管理模块，处理帖子的CRUD操作 | engines/FileEngine/post_manager.py |
| CommentManager | 评论管理模块，处理评论的添加和获取 | engines/FileEngine/comment_manager.py |
| QueueManager | 队列管理模块，处理异步操作 | engines/FileEngine/queue_manager.py |
| DatabaseManager | 数据库操作模块，管理帖子和评论的元数据 | engines/FileEngine/database.py |
| Logger | 日志管理模块，记录引擎运行日志 | engines/FileEngine/logger.py |
| APIRoutes | API路由定义，处理HTTP请求 | engines/FileEngine/api_routes.py |

### 3.2 数据存储结构

```
data/
└── FileEngine/
    ├── posts/                  # 帖子存储目录
    │   ├── post_id.md          # Markdown格式帖子
    │   ├── post_id.html        # HTML格式帖子（包含视频时自动使用）
    │   └── ...
    └── comments/               # 评论存储目录
        ├── hot/               # 热门评论（10秒内请求数超过10的帖子）
        │   ├── post_id.json    # 单个帖子的所有评论
        │   └── ...
        └── cold/              # 冷评论
            ├── comments_abc123.json  # 多个帖子的评论共用一个文件
            └── ...
```

### 3.3 技术栈

- **开发语言**：Python
- **存储方式**：文件系统（帖子和评论内容） + SQLite（元数据）
- **帖子格式**：Markdown和HTML
- **评论格式**：JSON
- **缓存机制**：内存缓存
- **队列机制**：本地队列（用于热门评论处理）

## 4. API 接口

### 4.1 引擎 API 接口

FileEngine引擎提供以下API接口，通过LinkGateway的服务代理调用：

#### 4.1.1 创建帖子

**功能**：创建新帖子

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "create_post",
  "data": {
    "title": "帖子标题",
    "content": "帖子内容"
  }
}
```

**返回**：
```json
{
  "post_id": "post_id",
  "file_path": "path/to/post/file.md",
  "file_type": "md",
  "status": "success"
}
```

#### 4.1.2 获取帖子

**功能**：根据ID获取帖子

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "get_post",
  "data": {
    "post_id": "post_id"
  }
}
```

**返回**：
```json
{
  "post_id": "post_id",
  "title": "帖子标题",
  "content": "帖子内容",
  "file_path": "path/to/post/file.md",
  "file_type": "md",
  "permission_level": "p0",
  "created_by": null,
  "is_public": true,
  "created_at": "2026-01-26T00:00:00",
  "updated_at": "2026-01-26T00:00:00",
  "status": "success"
}
```

#### 4.1.3 更新帖子

**功能**：更新帖子内容

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "update_post",
  "data": {
    "post_id": "post_id",
    "title": "更新后的帖子标题",
    "content": "更新后的帖子内容"
  }
}
```

**返回**：
```json
{
  "post_id": "post_id",
  "file_path": "path/to/post/file.md",
  "file_type": "md",
  "status": "success"
}
```

#### 4.1.4 删除帖子

**功能**：删除帖子

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "delete_post",
  "data": {
    "post_id": "post_id"
  }
}
```

**返回**：
```json
{
  "post_id": "post_id",
  "status": "success"
}
```

#### 4.1.5 添加评论

**功能**：为帖子添加评论

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "add_comment",
  "data": {
    "post_id": "post_id",
    "content": "评论内容",
    "author": "评论作者"
  }
}
```

**返回**：
```json
{
  "comment_id": "comment_id",
  "status": "success",
  "queue_processed": false
}
```

#### 4.1.6 获取评论

**功能**：获取帖子的评论

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "get_comments",
  "data": {
    "post_id": "post_id",
    "page": 1,
    "limit": 20
  }
}
```

**返回**：
```json
{
  "page": 1,
  "limit": 20,
  "total": 100,
  "comments": [
    {
      "id": "comment_id",
      "post_id": "post_id",
      "content": "评论内容",
      "author": "评论作者",
      "created_at": "2026-01-26T00:00:00",
      "updated_at": "2026-01-26T00:00:00"
    }
  ],
  "status": "success"
}
```

## 5. 配置参数

### 5.1 引擎配置

FileEngine的配置文件位于`engines/FileEngine/file_engine.json`，包含以下配置项：

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|-------|------|
| service_id | string | "FileEngine" | 服务ID |
| service_name | string | "文件处理引擎" | 服务名称 |
| version | string | "1.0.0" | 服务版本 |
| engine_type | string | "kernel" | 引擎类型 |
| description | string | "用于处理帖子和评论的文件存储与管理" | 服务描述 |
| apis | array | [] | API路由定义（目前未使用） |
| database | object | {"type": "sqlite", "name": "file_engine"} | 数据库配置 |
| dependencies | array | [] | 依赖服务列表 |

## 6. 部署与运行

### 6.1 集成方式

FileEngine引擎是LinkGateway生态系统的一部分，通过以下方式集成到系统中：

1. 将FileEngine目录放置在`engines/`目录下
2. LinkGateway启动时会自动发现并加载FileEngine引擎
3. 通过LinkGateway的服务代理调用FileEngine的API

### 6.2 启动服务

通过启动LinkGateway服务来间接启动FileEngine引擎：

```bash
# 进入后端目录
cd my_blog_backend

# 安装依赖
uv sync

# 启动LinkGateway服务
uv run python main.py
```

### 6.3 访问API

FileEngine引擎的API通过LinkGateway的服务代理进行访问，不直接暴露HTTP端点。

## 7. 开发指南

### 7.1 本地开发

1. 克隆代码库
2. 安装后端依赖
3. 运行LinkGateway服务
4. 通过LinkGateway的服务代理测试FileEngine引擎API

### 7.2 调试方法

- 使用VS Code或PyCharm进行调试
- 查看日志文件（log/FileEngine.log）
- 通过LinkGateway的API测试FileEngine功能

### 7.3 测试用例

FileEngine引擎内置了简单的测试功能，可以通过直接运行引擎文件进行测试：

```bash
python engines/FileEngine/file_engine.py
```

## 8. 最佳实践

### 8.1 性能优化

1. **冷热分离**：利用FileEngine的冷热分离特性，自动处理热门和冷帖子的评论存储
2. **批量操作**：对于大量评论的获取，使用分页机制减少内存占用
3. **日志级别设置**：在生产环境中适当调整日志级别，减少日志开销

### 8.2 数据安全

1. **定期备份**：定期备份帖子和评论文件
2. **权限控制**：设置适当的文件权限，防止未授权访问
3. **输入验证**：对用户输入进行严格验证，防止XSS攻击

## 9. 故障排除

### 9.1 常见问题

| 问题描述 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 帖子无法创建 | 目录权限问题 | 检查帖子存储目录的权限 |
| 评论无法提交 | 队列服务未运行 | 检查QueueManager是否正常运行 |
| 帖子访问缓慢 | 帖子内容过大 | 优化帖子内容，避免过大的文件 |

### 9.2 日志查看

FileEngine的日志文件位于`log/FileEngine.log`，可以通过查看日志文件了解系统运行情况和故障原因。

## 10. 版本历史

| 版本号 | 发布日期 | 主要变更 |
|-------|---------|---------|
| 1.0.0 | 2026-01-25 | 初始版本，包含帖子和评论管理功能 |

## 11. 贡献指南

欢迎对FileEngine进行贡献！如果你有任何建议或问题，可以通过以下方式联系我们：

- 提交Issue：在GitHub上提交Issue
- 提交Pull Request：提交代码改进

## 12. 许可证

FileEngine采用MIT许可证，详情请查看LICENSE文件。