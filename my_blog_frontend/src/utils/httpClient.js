/**
 * HTTP 客户端工具
 * 统一处理 API 请求,包括错误处理、Token 管理、请求拦截等
 */

import { API_BASE_URL, HTTP_STATUS, REQUEST_TIMEOUT } from '../config/apiConfig';
import { handleApiError } from './errorHandler';

/**
 * HTTP 客户端类
 */
class HttpClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = REQUEST_TIMEOUT;
  }

  /**
   * 获取认证 Token
   * @returns {string|null} Token
   */
  getToken() {
    return localStorage.getItem('authToken');
  }

  /**
   * 获取当前用户 ID
   * @returns {number|null} 用户 ID
   */
  getCurrentUserId() {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    const user = JSON.parse(userStr);
    return user.id || null;
  }

  /**
   * 构建请求头
   * @param {Object} customHeaders - 自定义请求头
   * @returns {Object} 请求头
   */
  buildHeaders(customHeaders = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...customHeaders
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * 处理响应
   * @param {Response} response - Fetch API 响应对象
   * @returns {Promise<Object>} 响应数据
   */
  async handleResponse(response) {
    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');

    if (!response.ok) {
      let errorData = {};
      
      if (isJson) {
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = { detail: { error: '解析错误响应失败' } };
        }
      }

      const errorMessage = errorData.detail?.error || errorData.error || `HTTP ${response.status}`;
      
      throw new Error(errorMessage);
    }

    if (isJson) {
      return await response.json();
    }

    return await response.text();
  }

  /**
   * 处理请求错误
   * @param {Error} error - 错误对象
   * @returns {Error} 处理后的错误
   */
  handleError(error) {
    return handleApiError(error);
  }

  /**
   * 发送 HTTP 请求
   * @param {string} url - 请求 URL
   * @param {Object} options - 请求选项
   * @returns {Promise<Object>} 响应数据
   */
  async request(url, options = {}) {
    const {
      method = 'GET',
      headers = {},
      body = null,
      timeout = this.timeout
    } = options;

    const requestOptions = {
      method,
      headers: this.buildHeaders(headers)
    };

    if (body) {
      requestOptions.body = JSON.stringify(body);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    requestOptions.signal = controller.signal;

    try {
      const response = await fetch(`${this.baseURL}${url}`, requestOptions);
      clearTimeout(timeoutId);
      return await this.handleResponse(response);
    } catch (error) {
      clearTimeout(timeoutId);
      throw this.handleError(error);
    }
  }

  /**
   * GET 请求
   * @param {string} url - 请求 URL
   * @param {Object} options - 请求选项
   * @returns {Promise<Object>} 响应数据
   */
  get(url, options = {}) {
    return this.request(url, { ...options, method: 'GET' });
  }

  /**
   * POST 请求
   * @param {string} url - 请求 URL
   * @param {Object} data - 请求数据
   * @param {Object} options - 请求选项
   * @returns {Promise<Object>} 响应数据
   */
  post(url, data, options = {}) {
    return this.request(url, { ...options, method: 'POST', body: data });
  }

  /**
   * PUT 请求
   * @param {string} url - 请求 URL
   * @param {Object} data - 请求数据
   * @param {Object} options - 请求选项
   * @returns {Promise<Object>} 响应数据
   */
  put(url, data, options = {}) {
    return this.request(url, { ...options, method: 'PUT', body: data });
  }

  /**
   * DELETE 请求
   * @param {string} url - 请求 URL
   * @param {Object} options - 请求选项
   * @returns {Promise<Object>} 响应数据
   */
  delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' });
  }

  /**
   * PATCH 请求
   * @param {string} url - 请求 URL
   * @param {Object} data - 请求数据
   * @param {Object} options - 请求选项
   * @returns {Promise<Object>} 响应数据
   */
  patch(url, data, options = {}) {
    return this.request(url, { ...options, method: 'PATCH', body: data });
  }
}

/**
 * 导出单例实例
 */
export const httpClient = new HttpClient();

/**
 * 导出默认类
 */
export default HttpClient;