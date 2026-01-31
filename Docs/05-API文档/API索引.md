# API 接口索引

## 1. API 概述

LinkGateway提供了完整的RESTful API接口，用于访问和管理系统中的各种资源。API接口采用分层设计，分为核心API、引擎API和业务API三个层级。所有API路径会自动进行标准化处理，确保格式一致。

## 2. API 分层设计

### 2.1 核心API

核心API提供了系统级别的功能，包括服务管理、健康检查等。

| API路径 | 方法 | 功能描述 | 文档位置 |
|---------|------|---------|---------|
| / | GET | 系统根路径 | - |
| /health | GET | 整体系统健康状态 | - |
| /health/services | GET | 服务健康状态 | - |
| /health/engines | GET | 引擎健康状态 | - |
| /services | GET | 列出所有服务 | - |
| /services/{service_id} | GET | 获取指定服务信息 | - |
| /services/{service_id}/health | GET | 检查单个服务健康状态 | - |
| /services/reload | POST | 重新加载所有服务 | - |
| /apis | GET | 列出所有API | - |
| /routes | GET | 列出所有路由 | - |
| /api-docs | GET | 获取API文档概览信息 | - |
| /interaction-rule | GET | 获取服务交互规则 | - |

### 2.2 引擎API

引擎API提供了各种引擎服务的功能，包括文件引擎、权限引擎等。

#### 2.2.1 FileEngine API

| API路径 | 方法 | 功能描述 | 文档位置 |
|---------|------|---------|---------|
| /api/file_engine/health | GET | 健康检查 | 引擎API/FileEngine.md |
| /api/file_engine/create_post | POST | 创建文章 | 引擎API/FileEngine.md |
| /api/file_engine/get_post | GET | 获取文章 | 引擎API/FileEngine.md |
| /api/file_engine/update_post | PUT | 更新文章 | 引擎API/FileEngine.md |
| /api/file_engine/delete_post | DELETE | 删除文章 | 引擎API/FileEngine.md |
| /api/file_engine/add_comment | POST | 添加评论 | 引擎API/FileEngine.md |
| /api/file_engine/get_comments | GET | 获取评论 | 引擎API/FileEngine.md |

#### 2.2.2 PermDog API

| API路径 | 方法 | 功能描述 | 文档位置 |
|---------|------|---------|---------|
| /api/permdog/health | GET | 健康检查 | 引擎API/PermDog.md |

### 2.3 业务API

业务API提供了各种业务服务的功能，包括用户管理、文章管理、互动管理等。

#### 2.3.1 User Server API

| API路径 | 方法 | 功能描述 | 文档位置 |
|---------|------|---------|---------|
| /api/user-server/register | POST | 用户注册 | 业务API/UserServer.md |
| /api/user-server/login | POST | 用户登录 | 业务API/UserServer.md |
| /api/user-server/users/{user_id} | GET | 获取用户信息 | 业务API/UserServer.md |
| /api/user-server/users/{user_id} | PUT | 更新用户信息 | 业务API/UserServer.md |
| /api/user-server/users/{user_id}/permissions | GET | 获取用户权限 | 业务API/UserServer.md |
| /api/user-server/users/{user_id}/pages | GET | 获取用户可访问页面 | 业务API/UserServer.md |
| /api/user-server/users/{user_id}/tasks | GET | 获取用户可访问任务 | 业务API/UserServer.md |
| /api/user-server/users/{user_id}/assets | GET | 获取用户资产列表 | 业务API/UserServer.md |
| /api/user-server/users/{user_id}/assets | POST | 创建用户资产 | 业务API/UserServer.md |
| /api/user-server/users/{user_id}/assets/{asset_id} | PUT | 更新用户资产 | 业务API/UserServer.md |
| /api/user-server/users/{user_id}/assets/{asset_id} | DELETE | 删除用户资产 | 业务API/UserServer.md |

#### 2.3.2 Post Service API

| API路径 | 方法 | 功能描述 | 文档位置 |
|---------|------|---------|---------|
| /api/post-service/posts | POST | 创建帖子 | 业务API/PostService.md |
| /api/post-service/posts | GET | 获取帖子列表 | 业务API/PostService.md |
| /api/post-service/posts/{post_id} | GET | 获取单个帖子 | 业务API/PostService.md |
| /api/post-service/posts/{post_id} | PUT | 更新帖子 | 业务API/PostService.md |
| /api/post-service/posts/{post_id} | DELETE | 删除帖子 | 业务API/PostService.md |

#### 2.3.3 Interaction Service API

| API路径 | 方法 | 功能描述 | 文档位置 |
|---------|------|---------|---------|
| /api/interaction-service/posts/{post_id}/like | POST | 点赞帖子 | 业务API/InteractionService.md |
| /api/interaction-service/posts/{post_id}/like | DELETE | 取消点赞 | 业务API/InteractionService.md |
| /api/interaction-service/posts/{post_id}/likes | GET | 获取帖子点赞数 | 业务API/InteractionService.md |
| /api/interaction-service/posts/{post_id}/comments | POST | 添加评论 | 业务API/InteractionService.md |
| /api/interaction-service/posts/{post_id}/comments | GET | 获取帖子评论 | 业务API/InteractionService.md |
| /api/interaction-service/comments/{comment_id} | DELETE | 删除评论 | 业务API/InteractionService.md |

## 3. API 认证

### 3.1 认证机制

LinkGateway采用JWT（JSON Web Token）作为认证机制，用于保护需要认证的API接口。

### 3.2 认证流程

1. 用户通过登录接口获取JWT令牌
2. 在后续的API请求中，将JWT令牌放在Authorization头中，格式为：`Bearer {token}`
3. 服务器验证JWT令牌的有效性
4. 如果令牌有效，处理API请求；否则，返回401 Unauthorized响应

### 3.3 认证范围

| API类型 | 是否需要认证 |
|---------|------------|
| 核心API | 否 |
| 引擎API | 部分需要 |
| 业务API | 大部分需要 |

## 4. API 响应格式

### 4.1 成功响应

成功响应的格式如下：

```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "message": "操作成功",
  "request_id": "req-123456"
}
```

### 4.2 错误响应

错误响应的格式如下：

```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "错误信息"
  },
  "message": "操作失败",
  "request_id": "req-123456"
}
```

### 4.3 常见错误码

| 错误码 | 描述 |
|-------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如API路径冲突） |
| 500 | 服务器内部错误 |
| 502 | 服务调用失败 |
| 503 | 服务不可用 |

## 5. API 版本控制

### 5.1 版本管理

LinkGateway的API采用URI版本控制，当前版本为v1。

### 5.2 版本兼容

- 向后兼容：新版本API兼容旧版本API
- 废弃机制：废弃的API会在文档中明确标记，并在适当的时间移除

## 6. API 调用方式

### 6.1 HTTP请求

通过HTTP客户端直接调用API：

```bash
# 使用curl调用API
curl -X POST http://localhost:8000/api/user-server/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'
```

### 6.2 服务代理调用

通过ServiceProxy进行服务间调用：

```python
from LinkGateway.service_proxy import ServiceProxy

# 创建服务代理
proxy = ServiceProxy()

# 调用业务服务
result = proxy.call_service(
    service_id="user-server",
    action="login",
    data={"username": "test", "password": "test"}
)

# 处理响应
if result["success"]:
    print("调用成功:", result["data"])
else:
    print("调用失败:", result["error"]["message"])
```

## 7. API 路径标准化

LinkGateway会自动对所有API路径进行标准化处理：

1. 确保路径以`/`开头
2. 移除重复的`/`
3. 标准化引擎和服务的路径格式
4. 检测并处理API路径冲突

## 8. API 使用指南

### 8.1 开发工具

- **API测试工具**：Postman、Insomnia等
- **HTTP客户端库**：requests（Python）、axios（JavaScript）等

### 8.2 最佳实践

1. **使用HTTPS**：在生产环境中使用HTTPS
2. **合理使用缓存**：对频繁访问的数据使用缓存
3. **分页查询**：对大量数据使用分页查询
4. **错误处理**：合理处理API错误
5. **日志记录**：记录API请求和响应日志
6. **请求ID**：使用请求ID跟踪请求流程
7. **服务标识**：在日志中包含服务标识符

## 9. API 文档索引

| 文档名称 | 描述 | 位置 |
|---------|------|------|
| API索引.md | API接口索引 | API/API索引.md |
| FileEngine.md | FileEngine API文档 | API/引擎API/FileEngine.md |
| PermDog.md | PermDog API文档 | API/引擎API/PermDog.md |
| UserServer.md | User Server API文档 | API/业务API/UserServer.md |
| PostService.md | Post Service API文档 | API/业务API/PostService.md |
| InteractionService.md | Interaction Service API文档 | API/业务API/InteractionService.md |

## 10. 贡献指南

欢迎对API文档进行贡献！如果你有任何建议或问题，可以通过以下方式联系我们：

- 提交Issue：在GitHub上提交Issue
- 提交Pull Request：提交代码改进
- 联系作者：发送邮件到作者邮箱

## 11. 许可证

API文档采用MIT许可证，详情请查看LICENSE文件。

---

**文档版本**：v2.0.0
**最后更新**：2026-01-30
**维护者**：MyBlog开发团队
