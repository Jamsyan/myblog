# Interaction Service API 文档

## 1. 服务概述

Interaction Service（互动服务）是MyBlog系统中的业务服务之一，负责处理用户与内容之间的互动功能，包括点赞和评论管理。

### 1.1 服务信息

| 属性 | 值 |
|-----|-----|
| service_id | interaction-service |
| service_name | 互动管理服务 |
| version | 1.0.0 |
| description | 负责帖子的评论和点赞功能管理 |

### 1.2 数据库配置

| 属性 | 值 |
|-----|-----|
| type | sqlite |
| name | user-server |

## 2. API 接口

### 2.1 点赞帖子

**接口描述**：点赞指定的帖子

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | POST |
| 路径 | /api/interaction-service/posts/{post_id}/like |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| post_id | string | 是 | 帖子ID |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/interaction-service/posts/123/like \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json"
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "post_id": "123",
    "liked": true,
    "like_count": 10
  },
  "message": "点赞成功",
  "request_id": "req-123456"
}
```

### 2.2 取消点赞

**接口描述**：取消对指定帖子的点赞

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | DELETE |
| 路径 | /api/interaction-service/posts/{post_id}/like |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| post_id | string | 是 | 帖子ID |

**请求示例**：

```bash
curl -X DELETE http://localhost:8000/api/interaction-service/posts/123/like \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json"
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "post_id": "123",
    "liked": false,
    "like_count": 9
  },
  "message": "取消点赞成功",
  "request_id": "req-123456"
}
```

### 2.3 获取帖子点赞数

**接口描述**：获取指定帖子的点赞数

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | GET |
| 路径 | /api/interaction-service/posts/{post_id}/likes |
| 认证 | 否 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| post_id | string | 是 | 帖子ID |

**请求示例**：

```bash
curl -X GET http://localhost:8000/api/interaction-service/posts/123/likes \
  -H "Content-Type: application/json"
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "post_id": "123",
    "like_count": 10
  },
  "message": "获取成功",
  "request_id": "req-123456"
}
```

### 2.4 添加评论

**接口描述**：为指定帖子添加评论

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | POST |
| 路径 | /api/interaction-service/posts/{post_id}/comments |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| post_id | string | 是 | 帖子ID |

**请求体**：

```json
{
  "content": "这是一条评论",
  "parent_id": null
}
```

**请求体参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| content | string | 是 | 评论内容 |
| parent_id | string | 否 | 父评论ID（回复评论时使用） |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/interaction-service/posts/123/comments \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "这是一条评论",
    "parent_id": null
  }'
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "comment_id": "456",
    "post_id": "123",
    "content": "这是一条评论",
    "author_id": "789",
    "created_at": "2026-01-30T10:30:00Z"
  },
  "message": "评论添加成功",
  "request_id": "req-123456"
}
```

### 2.5 获取帖子评论

**接口描述**：获取指定帖子的所有评论

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | GET |
| 路径 | /api/interaction-service/posts/{post_id}/comments |
| 认证 | 否 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| post_id | string | 是 | 帖子ID |

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|-----|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量 |

**请求示例**：

```bash
curl -X GET "http://localhost:8000/api/interaction-service/posts/123/comments?page=1&page_size=20" \
  -H "Content-Type: application/json"
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "comments": [
      {
        "comment_id": "456",
        "post_id": "123",
        "content": "这是一条评论",
        "author_id": "789",
        "author_name": "张三",
        "created_at": "2026-01-30T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 50,
      "page": 1,
      "page_size": 20,
      "total_pages": 3
    }
  },
  "message": "获取成功",
  "request_id": "req-123456"
}
```

### 2.6 删除评论

**接口描述**：删除指定的评论

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | DELETE |
| 路径 | /api/interaction-service/comments/{comment_id} |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| comment_id | string | 是 | 评论ID |

**请求示例**：

```bash
curl -X DELETE http://localhost:8000/api/interaction-service/comments/456 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json"
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "comment_id": "456",
    "deleted": true
  },
  "message": "评论删除成功",
  "request_id": "req-123456"
}
```

## 3. 错误码

| 错误码 | 描述 | 解决方案 |
|-------|------|--------|
| 400 | 请求参数错误 | 检查请求参数是否正确 |
| 401 | 未授权 | 检查Token是否有效 |
| 403 | 禁止访问 | 检查是否有权限执行该操作 |
| 404 | 资源不存在 | 检查帖子或评论ID是否正确 |
| 500 | 服务器内部错误 | 联系系统管理员 |

## 4. 使用示例

### 4.1 JavaScript/axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// 点赞帖子
async function likePost(postId) {
  try {
    const response = await api.post(`/api/interaction-service/posts/${postId}/like`);
    console.log('点赞成功:', response.data);
  } catch (error) {
    console.error('点赞失败:', error);
  }
}

// 添加评论
async function addComment(postId, content) {
  try {
    const response = await api.post(`/api/interaction-service/posts/${postId}/comments`, {
      content: content
    });
    console.log('评论添加成功:', response.data);
  } catch (error) {
    console.error('评论添加失败:', error);
  }
}
```

### 4.2 Python/requests

```python
import requests

API_BASE_URL = "http://localhost:8000"
TOKEN = "your_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 点赞帖子
def like_post(post_id):
    url = f"{API_BASE_URL}/api/interaction-service/posts/{post_id}/like"
    response = requests.post(url, headers=headers)
    return response.json()

# 添加评论
def add_comment(post_id, content):
    url = f"{API_BASE_URL}/api/interaction-service/posts/{post_id}/comments"
    data = {
        "content": content
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
```

## 5. 注意事项

1. **认证要求**：点赞和添加评论需要用户认证
2. **权限控制**：用户只能删除自己的评论
3. **数据验证**：评论内容不能为空，长度限制为1-1000字符
4. **频率限制**：为防止刷屏，对点赞和评论操作实施频率限制
5. **敏感词过滤**：评论内容会进行敏感词过滤

## 6. 未来扩展

计划中的功能：

- [ ] 评论回复功能
- [ ] 评论点赞功能
- [ ] 评论举报功能
- [ ] 点赞通知
- [ ] 评论@提醒功能

---

**文档版本**：v2.0.0
**最后更新**：2026-01-30
**维护者**：MyBlog开发团队
