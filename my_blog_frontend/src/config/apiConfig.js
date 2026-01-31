/**
 * API 配置文件
 * 统一管理 API 基础 URL 和请求配置
 */

// 基础 API URL (开发环境使用代理,生产环境需要配置完整 URL)
export const API_BASE_URL = '/api';

/**
 * API 端点配置
 */
export const API_ENDPOINTS = {
  // 用户服务
  USER_SERVER: {
    LOGIN: '/user-server/login',
    REGISTER: '/user-server/register',
    GET_USER: '/user-server/users',
    UPDATE_USER: '/user-server/users',
    GET_PERMISSIONS: '/user-server/users',
    GET_PAGES: '/user-server/users',
    GET_TASKS: '/user-server/users',
    GET_ASSETS: '/user-server/users',
    CREATE_ASSET: '/user-server/users',
    UPDATE_ASSET: '/user-server/users',
    DELETE_ASSET: '/user-server/users'
  },
  // 文章服务
  POST_SERVICE: {
    GET_POSTS: '/post-service/posts',
    GET_POST: '/post-service/posts',
    CREATE_POST: '/post-service/posts',
    UPDATE_POST: '/post-service/posts',
    DELETE_POST: '/post-service/posts'
  },
  // 互动服务
  INTERACTION_SERVICE: {
    LIKE_POST: '/interaction-service/posts',
    GET_LIKES: '/interaction-service/posts',
    CREATE_COMMENT: '/interaction-service/posts',
    GET_COMMENTS: '/interaction-service/posts',
    DELETE_COMMENT: '/interaction-service/comments'
  }
};

/**
 * HTTP 状态码
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
};

/**
 * 请求超时时间 (毫秒)
 */
export const REQUEST_TIMEOUT = 30000;

/**
 * 获取完整的 API URL
 * @param {string} endpoint - API 端点
 * @returns {string} 完整的 API URL
 */
export const getApiUrl = (endpoint) => {
  return `${API_BASE_URL}${endpoint}`;
};