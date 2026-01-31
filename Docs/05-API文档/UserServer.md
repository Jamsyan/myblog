# UserServer 服务文档

## 1. 服务概述

UserServer（用户服务）是MyBlog系统中的业务服务之一，负责用户注册、登录、权限管理和资产管理。

### 1.1 服务信息

| 属性 | 值 |
|-----|-----|
| service_id | user-server |
| service_name | 用户服务器 |
| version | 1.0.0 |
| description | 负责用户注册、登录、权限管理和资产管理 |

### 1.2 数据库配置

| 属性 | 值 |
|-----|-----|
| type | sqlite |
| name | user-server |

## 2. API 接口

### 2.1 用户注册

**接口描述**：注册新用户

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | POST |
| 路径 | /api/user-server/register |
| 认证 | 否 |

**请求体**：

```json
{
  "username": "testuser",
  "password": "password123",
  "email": "test@example.com"
}
```

**请求体参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| username | string | 是 | 用户名（3-20字符） |
| password | string | 是 | 密码（6-20字符） |
| email | string | 是 | 邮箱地址 |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "user_id": "123",
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2026-01-30T10:30:00Z"
  },
  "message": "注册成功",
  "request_id": "req-123456"
}
```

### 2.2 用户登录

**接口描述**：用户登录获取访问令牌

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | POST |
| 路径 | /api/user-server/login |
| 认证 | 否 |

**请求体**：

```json
{
  "username": "testuser",
  "password": "password123"
}
```

**请求体参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_id": "123",
    "username": "testuser",
    "expires_in": 86400
  },
  "message": "登录成功",
  "request_id": "req-123456"
}
```

### 2.3 获取用户信息

**接口描述**：获取指定用户的详细信息

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | GET |
| 路径 | /api/user-server/users/{user_id} |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| user_id | string | 是 | 用户ID |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "user_id": "123",
    "username": "testuser",
    "email": "test@example.com",
    "avatar_url": "https://example.com/avatar/123.jpg",
    "bio": "这是我的个人简介",
    "created_at": "2026-01-30T10:30:00Z",
    "updated_at": "2026-01-30T10:30:00Z"
  },
  "message": "获取成功",
  "request_id": "req-123456"
}
```

### 2.4 更新用户信息

**接口描述**：更新指定用户的信息

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | PUT |
| 路径 | /api/user-server/users/{user_id} |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| user_id | string | 是 | 用户ID |

**请求体**：

```json
{
  "email": "newemail@example.com",
  "bio": "更新后的个人简介",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

**请求体参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| email | string | 否 | 邮箱地址 |
| bio | string | 否 | 个人简介（最多500字符） |
| avatar_url | string | 否 | 头像URL |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "user_id": "123",
    "username": "testuser",
    "email": "newemail@example.com",
    "avatar_url": "https://example.com/new-avatar.jpg",
    "bio": "更新后的个人简介",
    "updated_at": "2026-01-30T11:00:00Z"
  },
  "message": "更新成功",
  "request_id": "req-123456"
}
```

### 2.5 获取用户权限

**接口描述**：获取指定用户的权限列表

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | GET |
| 路径 | /api/user-server/users/{user_id}/permissions |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| user_id | string | 是 | 用户ID |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "user_id": "123",
    "permissions": [
      "post:create",
      "post:edit",
      "post:delete",
      "comment:create",
      "comment:delete",
      "like:create",
      "user:profile:edit"
    ]
  },
  "message": "获取成功",
  "request_id": "req-123456"
}
```

### 2.6 获取用户可访问页面

**接口描述**：获取指定用户可以访问的页面列表

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | GET |
| 路径 | /api/user-server/users/{user_id}/pages |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| user_id | string | 是 | 用户ID |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "user_id": "123",
    "pages": [
      "/",
      "/explore",
      "/explore/post/:id",
      "/profile"
    ]
  },
  "message": "获取成功",
  "request_id": "req-123456"
}
```

### 2.7 获取用户可访问任务

**接口描述**：获取指定用户可以执行的任务列表

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | GET |
| 路径 | /api/user-server/users/{user_id}/tasks |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| user_id | string | 是 | 用户ID |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "user_id": "123",
    "tasks": [
      "create_post",
      "edit_post",
      "delete_post",
      "like_post",
      "comment_post"
    ]
  },
  "message": "获取成功",
  "request_id": "req-123456"
}
```

### 2.8 获取用户资产列表

**接口描述**：获取指定用户的资产列表

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | GET |
| 路径 | /api/user-server/users/{user_id}/assets |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| user_id | string | 是 | 用户ID |

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|-----|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量 |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "assets": [
      {
        "asset_id": "456",
        "type": "image",
        "name": "avatar.jpg",
        "url": "https://example.com/assets/avatar.jpg",
        "size": 102400,
        "created_at": "2026-01-30T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 10,
      "page": 1,
      "page_size": 20,
      "total_pages": 1
    }
  },
  "message": "获取成功",
  "request_id": "req-123456"
}
```

### 2.9 创建用户资产

**接口描述**：为指定用户创建新资产

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | POST |
| 路径 | /api/user-server/users/{user_id}/assets |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| user_id | string | 是 | 用户ID |

**请求体**：

```json
{
  "type": "image",
  "name": "new-avatar.jpg",
  "file_data": "base64_encoded_data"
}
```

**请求体参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| type | string | 是 | 资产类型（image、video、document等） |
| name | string | 是 | 资产名称 |
| file_data | string | 是 | 文件数据（Base64编码） |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "asset_id": "457",
    "type": "image",
    "name": "new-avatar.jpg",
    "url": "https://example.com/assets/new-avatar.jpg",
    "size": 102400,
    "created_at": "2026-01-30T11:00:00Z"
  },
  "message": "创建成功",
  "request_id": "req-123456"
}
```

### 2.10 更新用户资产

**接口描述**：更新指定的用户资产

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | PUT |
| 路径 | /api/user-server/users/{user_id}/assets/{asset_id} |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| user_id | string | 是 | 用户ID |
| asset_id | string | 是 | 资产ID |

**请求体**：

```json
{
  "name": "updated-avatar.jpg"
}
```

**请求体参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| name | string | 否 | 资产名称 |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "asset_id": "457",
    "type": "image",
    "name": "updated-avatar.jpg",
    "url": "https://example.com/assets/updated-avatar.jpg",
    "updated_at": "2026-01-30T11:30:00Z"
  },
  "message": "更新成功",
  "request_id": "req-123456"
}
```

### 2.11 删除用户资产

**接口描述**：删除指定的用户资产

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | DELETE |
| 路径 | /api/user-server/users/{user_id}/assets/{asset_id} |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| user_id | string | 是 | 用户ID |
| asset_id | string | 是 | 资产ID |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "asset_id": "457",
    "deleted": true
  },
  "message": "删除成功",
  "request_id": "req-123456"
}
```

## 3. 错误码

| 错误码 | 描述 | 解决方案 |
|-------|------|--------|
| 400 | 请求参数错误 | 检查请求参数是否正确 |
| 401 | 未授权 | 检查Token是否有效 |
| 403 | 禁止访问 | 检查是否有权限执行该操作 |
| 404 | 资源不存在 | 检查用户ID或资产ID是否正确 |
| 409 | 资源冲突 | 用户名或邮箱已存在 |
| 500 | 服务器内部错误 | 联系系统管理员 |

## 4. 使用示例

### 4.1 JavaScript/axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 用户登录
async function login(username, password) {
  try {
    const response = await api.post('/api/user-server/login', {
      username,
      password
    });
    console.log('登录成功:', response.data);
    return response.data.data.token;
  } catch (error) {
    console.error('登录失败:', error);
    throw error;
  }
}

// 获取用户信息
async function getUserInfo(userId, token) {
  try {
    const response = await api.get(`/api/user-server/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    console.log('获取成功:', response.data);
    return response.data.data;
  } catch (error) {
    console.error('获取失败:', error);
    throw error;
  }
}
```

### 4.2 Python/requests

```python
import requests

API_BASE_URL = "http://localhost:8000"

headers = {
    "Content-Type": "application/json"
}

# 用户登录
def login(username, password):
    url = f"{API_BASE_URL}/api/user-server/login"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 获取用户信息
def get_user_info(user_id, token):
    url = f"{API_BASE_URL}/api/user-server/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()
```

## 5. 注意事项

1. **密码安全**：密码在传输和存储时都应该加密
2. **Token管理**：JWT Token应该妥善保管，过期后需要重新登录
3. **权限控制**：用户只能访问和修改自己的资源
4. **数据验证**：所有输入数据都应该进行验证
5. **频率限制**：为防止暴力破解，对登录和注册操作实施频率限制

## 6. 未来扩展

计划中的功能：

- [ ] 第三方登录（GitHub、Google等）
- [ ] 密码找回功能
- [ ] 邮箱验证功能
- [ ] 用户等级系统
- [ ] 用户积分系统

---

**文档版本**：v2.0.0
**最后更新**：2026-01-30
**维护者**：MyBlog开发团队
