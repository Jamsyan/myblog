# PermDog 文档

## 1. 引擎简介

PermDog是LinkGateway内置的权限管理引擎，专注于提供权限定义、配置和验证功能。它采用基于权限等级的模型，通过权限等级来管理不同用户的操作权限和组件访问权限，不直接处理用户或角色管理。

## 2. 功能特性

### 2.1 权限管理

- **权限定义**：支持操作和组件的权限定义
- **权限配置**：支持为不同权限等级配置允许的操作和组件
- **权限验证**：支持运行时检查操作权限和组件访问权限
- **权限等级**：支持多个权限等级，从p0（最高权限）到p3（最低权限）

### 2.2 权限等级管理

- **默认权限**：支持设置默认权限等级
- **权限热更新**：支持动态重新加载权限配置，无需重启服务
- **权限预加载**：支持启动时预加载所有权限配置到内存，提高性能

### 2.3 操作与组件管理

- **操作注册**：支持注册系统中的各种操作
- **组件注册**：支持注册前端组件，用于控制组件访问权限

### 2.4 其他功能

- **健康检查**：支持引擎健康状态检查
- **元数据获取**：支持获取引擎元数据信息

## 3. 技术架构

### 3.1 核心组件

| 组件名称 | 功能描述 | 文件位置 |
|---------|---------|---------|
| PermDogEngine | 引擎主类，协调各个模块工作 | engines/PermDog/permdog.py |
| PermissionManager | 权限管理模块，处理权限配置和验证 | engines/PermDog/permission_manager.py |
| DatabaseManager | 数据库操作模块，管理权限等级数据 | engines/PermDog/database.py |
| Logger | 日志管理模块，记录引擎运行日志 | engines/PermDog/logger.py |
| APIRoutes | API路由定义，处理HTTP请求 | engines/PermDog/api_routes.py |

### 3.2 数据存储结构

```
data/
└── permdog/
    └── permissions/           # 权限存储目录
        ├── p0.json            # p0权限配置文件
        ├── p1.json            # p1权限配置文件
        ├── p2.json            # p2权限配置文件
        └── p3.json            # p3权限配置文件
```

### 3.3 技术栈

- **开发语言**：Python
- **存储方式**：文件系统（权限配置） + SQLite（权限等级数据）
- **权限格式**：JSON
- **缓存机制**：内存缓存
- **日志系统**：自定义日志管理器
- **Web框架**：FastAPI（通过LinkGateway集成）

## 4. API 接口

### 4.1 引擎 API 接口

PermDog引擎提供以下API接口，通过LinkGateway进行调用：

#### 4.1.1 注册操作

**功能**：注册系统中的操作，用于权限控制

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "register_operation",
  "data": {
    "operation_name": "create_post",
    "description": "创建帖子"
  }
}
```

**返回**：
```json
{
  "message": "Operation 'create_post' registered successfully",
  "operation_name": "create_post",
  "status": "success"
}
```

#### 4.1.2 注册组件

**功能**：注册前端组件，用于控制组件访问权限

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "register_component",
  "data": {
    "component_id": "user_management",
    "component_name": "用户管理",
    "description": "用户管理页面"
  }
}
```

**返回**：
```json
{
  "message": "Component '用户管理' registered successfully",
  "component_id": "user_management",
  "component_name": "用户管理",
  "status": "success"
}
```

#### 4.1.3 获取默认权限

**功能**：获取系统默认的权限等级

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "get_default_permission",
  "data": {}
}
```

**返回**：
```json
{
  "permission_level": "p3",
  "name": "默认权限",
  "status": "success"
}
```

#### 4.1.4 检查操作权限

**功能**：检查指定权限等级是否有权执行某个操作

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "check_operation_permission",
  "data": {
    "permission_level": "p1",
    "operation_name": "create_post"
  }
}
```

**返回**：
```json
{
  "allowed": true,
  "permission_level": "p1",
  "operation_name": "create_post",
  "status": "success"
}
```

#### 4.1.5 检查组件权限

**功能**：检查指定权限等级是否有权访问某个组件

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "check_component_permission",
  "data": {
    "permission_level": "p1",
    "component_id": "user_management"
  }
}
```

**返回**：
```json
{
  "allowed": true,
  "permission_level": "p1",
  "component_id": "user_management",
  "status": "success"
}
```

#### 4.1.6 获取权限配置

**功能**：获取指定权限等级的配置

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "get_permission_config",
  "data": {
    "permission_level": "p1"
  }
}
```

**返回**：
```json
{
  "config": {
    "permission_level": "p1",
    "name": "管理员权限",
    "allowed_operations": ["create_post", "update_post"],
    "allowed_components": ["user_management"],
    "created_at": "2026-01-26T12:00:00",
    "updated_at": "2026-01-26T12:00:00"
  },
  "status": "success"
}
```

#### 4.1.7 更新权限配置

**功能**：更新指定权限等级的配置

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "update_permission_config",
  "data": {
    "permission_level": "p1",
    "allowed_operations": ["create_post", "update_post", "delete_post"],
    "allowed_components": ["user_management", "post_management"]
  }
}
```

**返回**：
```json
true
```

#### 4.1.8 设置默认权限

**功能**：设置系统默认的权限等级

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "set_default_permission",
  "data": {
    "permission_level": "p2"
  }
}
```

**返回**：
```json
{
  "message": "Default permission level set to 'p2'",
  "status": "success"
}
```

#### 4.1.9 重新加载权限

**功能**：重新加载所有权限配置到内存（热更新）

**调用方式**：通过LinkGateway的服务代理调用

**参数**：
```json
{
  "action": "reload_permissions",
  "data": {
    "user_permission_level": "p0"  // 只有p0级用户可以调用此接口
  }
}
```

**返回**：
```json
{
  "message": "Permissions reloaded successfully",
  "status": "success"
}
```

## 5. 配置参数

### 5.1 引擎配置

PermDog的配置文件位于`engines/PermDog/permdog.json`，包含以下配置项：

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|-------|------|
| service_id | string | "permdog" | 服务ID |
| service_name | string | "权限引擎" | 服务名称 |
| version | string | "1.0.0" | 服务版本 |
| engine_type | string | "kernel" | 引擎类型 |
| description | string | "用于管理系统权限体系的引擎，支持权限查询、权限检查和权限配置管理" | 服务描述 |
| apis | array | [] | API路由定义（目前未使用） |
| database | object | {"type": "sqlite", "name": "permdog"} | 数据库配置 |
| dependencies | array | [] | 依赖服务列表 |

### 5.2 运行时配置

PermDog引擎在运行时会使用以下默认配置：

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|-------|------|
| permission_dir | string | "data/permdog/permissions" | 权限存储目录 |
| db_path | string | "data/permdog/permdog.db" | 数据库文件路径 |
| log_path | string | "log/permdog.log" | 日志文件路径 |

## 6. 部署与运行

### 6.1 集成方式

PermDog引擎是LinkGateway生态系统的一部分，通过以下方式集成到系统中：

1. 将PermDog目录放置在`engines/`目录下
2. LinkGateway启动时会自动发现并加载PermDog引擎
3. 通过LinkGateway的服务代理调用PermDog的API

### 6.2 启动服务

通过启动LinkGateway服务来间接启动PermDog引擎：

```bash
# 进入后端目录
cd my_blog_backend

# 安装依赖
uv sync

# 启动LinkGateway服务
uv run python main.py
```

### 6.3 访问API

PermDog引擎的API通过LinkGateway的服务代理进行访问，不直接暴露HTTP端点。

## 7. 开发指南

### 7.1 本地开发

1. 克隆代码库
2. 安装后端依赖
3. 运行LinkGateway服务
4. 通过LinkGateway的服务代理测试PermDog引擎API

### 7.2 调试方法

- 使用VS Code或PyCharm进行调试
- 查看日志文件（log/permdog.log）
- 通过LinkGateway的API测试PermDog功能

### 7.3 测试用例

PermDog引擎内置了简单的测试功能，可以通过直接运行引擎文件进行测试：

```bash
python engines/PermDog/permdog.py
```

## 8. 最佳实践

### 8.1 权限设计

1. **最小权限原则**：只授予用户必要的权限等级
2. **权限等级分明**：合理划分p0-p3权限等级
3. **定期审计**：定期检查权限配置，确保权限设置合理
4. **权限热更新**：使用权限热更新功能，无需重启服务即可更新权限配置

### 8.2 性能优化

1. **权限预加载**：引擎启动时会预加载所有权限配置到内存，提高权限验证速度
2. **合理设计权限等级**：避免过多权限等级，减少权限检查的复杂度
3. **日志级别设置**：在生产环境中适当调整日志级别，减少日志开销

### 8.3 安全建议

1. **权限等级保护**：确保只有高权限用户可以修改权限配置
2. **输入验证**：对注册的操作和组件进行严格的输入验证
3. **日志记录**：开启日志记录，便于追踪权限操作

## 9. 故障排除

### 9.1 常见问题

| 问题描述 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 权限验证失败 | 权限等级配置错误 | 检查权限等级配置，确保操作或组件已添加到允许列表 |
| 权限热更新失败 | 用户权限不足 | 确保只有p0级用户可以调用权限热更新接口 |
| 引擎启动失败 | 目录权限问题 | 检查权限存储目录的权限，确保引擎有读写权限 |

### 9.2 日志查看

PermDog的日志文件位于`log/permdog.log`，可以通过查看日志文件了解系统运行情况和故障原因。

### 9.3 数据恢复

如果发生权限数据丢失，可以通过以下步骤恢复数据：

1. 停止LinkGateway服务
2. 恢复权限配置文件到`data/permdog/permissions/`目录
3. 启动LinkGateway服务
4. 验证权限配置是否恢复正常

## 10. 版本历史

| 版本号 | 发布日期 | 主要变更 |
|-------|---------|---------|
| 1.0.0 | 2026-01-25 | 初始版本，包含权限配置、权限验证和权限等级管理功能 |

## 11. 贡献指南

欢迎对PermDog进行贡献！如果你有任何建议或问题，可以通过以下方式联系我们：

- 提交Issue：在GitHub上提交Issue
- 提交Pull Request：提交代码改进

## 12. 许可证

PermDog采用MIT许可证，详情请查看LICENSE文件。