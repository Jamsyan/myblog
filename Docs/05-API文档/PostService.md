# PostService 服务文档

## 1. 服务概述

PostService（文章服务）是MyBlog系统中的业务服务之一，负责帖子的创建、查询、更新和删除，以及基于权限的帖子可见性控制。

### 1.1 服务信息

| 属性 | 值 |
|-----|-----|
| service_id | post-service |
| service_name | 帖子管理服务 |
| version | 1.0.0 |
| description | 负责帖子的创建、查询、更新和删除，以及基于权限的帖子可见性控制 |

### 1.2 数据库配置

| 属性 | 值 |
|-----|-----|
| type | sqlite |
| name | user-server |

## 2. API 接口

### 2.1 创建帖子

**接口描述**：创建新帖子

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | POST |
| 路径 | /api/post-service/posts |
| 认证 | 是 |

**请求体**：

```json
{
  "title": "我的第一篇博客",
  "content": "这是博客内容...",
  "summary": "博客摘要",
  "tags": ["技术", "生活"],
  "visibility": "public"
}
```

**请求体参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| title | string | 是 | 帖子标题（1-100字符） |
| content | string | 是 | 帖子内容（Markdown格式） |
| summary | string | 否 | 帖子摘要（1-200字符） |
| tags | array | 否 | 标签列表（最多10个） |
| visibility | string | 否 | 可见性（public、private、followers） |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "post_id": "123",
    "title": "我的第一篇博客",
    "content": "这是博客内容...",
    "summary": "博客摘要",
    "tags": ["技术", "生活"],
    "visibility": "public",
    "author_id": "456",
    "created_at": "2026-01-30T10:30:00Z",
    "updated_at": "2026-01-30T10:30:00Z"
  },
  "message": "创建成功",
  "request_id": "req-123456"
}
```

### 2.2 获取帖子列表

**接口描述**：获取帖子列表，支持分页和筛选

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | GET |
| 路径 | /api/post-service/posts |
| 认证 | 否 |

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|-----|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量 |
| author_id | string | 否 | - | 按作者筛选 |
| tag | string | 否 | - | 按标签筛选 |
| visibility | string | 否 | public | 按可见性筛选 |
| sort_by | string | 否 | created_at | 排序字段（created_at、updated_at） |
| sort_order | string | 否 | desc | 排序顺序（asc、desc） |

**请求示例**：

```bash
curl -X GET "http://localhost:8000/api/post-service/posts?page=1&page_size=20&sort_by=created_at&sort_order=desc" \
  -H "Content-Type: application/json"
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "post_id": "123",
        "title": "我的第一篇博客",
        "summary": "博客摘要",
        "tags": ["技术", "生活"],
        "visibility": "public",
        "author_id": "456",
        "author_name": "张三",
        "created_at": "2026-01-30T10:30:00Z",
        "updated_at": "2026-01-30T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 100,
      "page": 1,
      "page_size": 20,
      "total_pages": 5
    }
  },
  "message": "获取成功",
  "request_id": "req-123456"
}
```

### 2.3 获取单个帖子

**接口描述**：获取指定帖子的详细信息

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | GET |
| 路径 | /api/post-service/posts/{post_id} |
| 认证 | 否 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| post_id | string | 是 | 帖子ID |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "post_id": "123",
    "title": "我的第一篇博客",
    "content": "这是博客内容...",
    "summary": "博客摘要",
    "tags": ["技术", "生活"],
    "visibility": "public",
    "author_id": "456",
    "author_name": "张三",
    "author_avatar": "https://example.com/avatar/456.jpg",
    "created_at": "2026-01-30T10:30:00Z",
    "updated_at": "2026-01-30T10:30:00Z",
    "view_count": 100,
    "like_count": 10,
    "comment_count": 5
  },
  "message": "获取成功",
  "request_id": "req-123456"
}
```

### 2.4 更新帖子

**接口描述**：更新指定的帖子

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | PUT |
| 路径 | /api/post-service/posts/{post_id} |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| post_id | string | 是 | 帖子ID |

**请求体**：

```json
{
  "title": "更新后的标题",
  "content": "更新后的内容...",
  "summary": "更新后的摘要",
  "tags": ["技术", "更新"],
  "visibility": "public"
}
```

**请求体参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| title | string | 否 | 帖子标题 |
| content | string | 否 | 帖子内容 |
| summary | string | 否 | 帖子摘要 |
| tags | array | 否 | 标签列表 |
| visibility | string | 否 | 可见性 |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "post_id": "123",
    "title": "更新后的标题",
    "content": "更新后的内容...",
    "summary": "更新后的摘要",
    "tags": ["技术", "更新"],
    "visibility": "public",
    "updated_at": "2026-01-30T11:00:00Z"
  },
  "message": "更新成功",
  "request_id": "req-123456"
}
```

### 2.5 删除帖子

**接口描述**：删除指定的帖子

**请求信息**：

| 属性 | 值 |
|-----|-----|
| 方法 | DELETE |
| 路径 | /api/post-service/posts/{post_id} |
| 认证 | 是 |

**路径参数**：

| 参数 | 类型 | 必填 | 描述 |
|-----|------|------|------|
| post_id | string | 是 | 帖子ID |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "post_id": "123",
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
| 404 | 资源不存在 | 检查帖子ID是否正确 |
| 500 | 服务器内部错误 | 联系系统管理员 |

## 4. 使用示例

### 4.1 JavaScript/axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// 创建帖子
async function createPost(postData) {
  try {
    const response = await api.post('/api/post-service/posts', postData);
    console.log('创建成功:', response.data);
    return response.data.data;
  } catch (error) {
    console.error('创建失败:', error);
    throw error;
  }
}

// 获取帖子列表
async function getPosts(page = 1, pageSize = 20) {
  try {
    const response = await api.get('/api/post-service/posts', {
      params: {
        page,
        page_size: pageSize
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
TOKEN = "your_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 创建帖子
def create_post(post_data):
    url = f"{API_BASE_URL}/api/post-service/posts"
    response = requests.post(url, json=post_data, headers=headers)
    return response.json()

# 获取帖子列表
def get_posts(page=1, page_size=20):
    url = f"{API_BASE_URL}/api/post-service/posts"
    params = {
        "page": page,
        "page_size": page_size
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()
```

## 5. 注意事项

1. **权限控制**：用户只能更新和删除自己的帖子
2. **内容验证**：帖子内容应该进行XSS过滤和敏感词过滤
3. **Markdown支持**：帖子内容支持Markdown格式
4. **标签管理**：标签应该规范化，避免重复
5. **可见性控制**：根据帖子可见性控制访问权限

## 6. 未来扩展

计划中的功能：

- [ ] 帖子草稿功能
- [ ] 帖子定时发布
- [ ] 帖子置顶功能
- [ ] 帖子推荐功能
- [ ] 帖子搜索功能
- [ ] 帖子分享功能

---

**文档版本**：v2.0.0
**最后更新**：2026-01-30
**维护者**：MyBlog开发团队
