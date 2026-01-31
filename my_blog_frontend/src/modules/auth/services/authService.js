/**
 * 认证服务
 * 处理登录、注册等认证相关的 API 调用
 */

import { httpClient } from '../../../utils/httpClient';
import { API_ENDPOINTS } from '../../../config/apiConfig';

/**
 * 登录请求
 * @param {Object} credentials - 登录凭证
 * @param {string} credentials.username - 用户名或邮箱
 * @param {string} credentials.password - 密码
 * @returns {Promise<Object>} 登录结果
 */
export const login = async (credentials) => {
  try {
    const result = await httpClient.post(API_ENDPOINTS.USER_SERVER.LOGIN, credentials);

    if (result.user) {
      localStorage.setItem('user', JSON.stringify(result.user));
      localStorage.setItem('permissions', JSON.stringify(result.permissions || []));
      localStorage.setItem('isLoggedIn', 'true');
      
      if (result.token) {
        localStorage.setItem('authToken', result.token);
      }
    }

    return result;
  } catch (error) {
    console.error('登录失败:', error);
    throw error;
  }
};

/**
 * 注册请求
 * @param {Object} userData - 用户注册数据
 * @param {string} userData.username - 用户名
 * @param {string} userData.email - 邮箱
 * @param {string} userData.password - 密码
 * @param {string} userData.full_name - 完整名称(可选)
 * @returns {Promise<Object>} 注册结果
 */
export const register = async (userData) => {
  try {
    const result = await httpClient.post(API_ENDPOINTS.USER_SERVER.REGISTER, userData);
    return result;
  } catch (error) {
    console.error('注册失败:', error);
    throw error;
  }
};

/**
 * 登出
 */
export const logout = () => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
  localStorage.removeItem('permissions');
  localStorage.removeItem('isLoggedIn');
};

/**
 * 获取当前登录用户信息
 * @returns {Object|null} 用户信息
 */
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * 检查是否已登录
 * @returns {boolean} 是否已登录
 */
export const isAuthenticated = () => {
  return localStorage.getItem('isLoggedIn') === 'true';
};

/**
 * 获取认证 token
 * @returns {string|null} 认证 token
 */
export const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

/**
 * 获取用户权限列表
 * @returns {Array} 权限列表
 */
export const getUserPermissions = () => {
  const permissionsStr = localStorage.getItem('permissions');
  return permissionsStr ? JSON.parse(permissionsStr) : [];
};

/**
 * 检查用户是否有指定权限
 * @param {string} permission - 权限名称
 * @returns {boolean} 是否有权限
 */
export const hasPermission = (permission) => {
  const permissions = getUserPermissions();
  return permissions.includes(permission);
};

/**
 * 获取用户 ID
 * @returns {number|null} 用户 ID
 */
export const getUserId = () => {
  const user = getCurrentUser();
  return user ? user.id : null;
};

/**
 * 获取用户权限级别
 * @returns {string|null} 权限级别 (P0-P3)
 */
export const getPermissionLevel = () => {
  const user = getCurrentUser();
  return user ? user.permission_level : null;
};

/**
 * 检查用户是否可以访问指定权限级别的内容
 * @param {string} requiredLevel - 需要的权限级别
 * @returns {boolean} 是否可以访问
 */
export const canAccessLevel = (requiredLevel) => {
  const userLevel = getPermissionLevel();
  if (!userLevel) return false;

  const levelMap = { 'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3 };
  const userLevelValue = levelMap[userLevel] || 0;
  const requiredLevelValue = levelMap[requiredLevel] || 0;

  return userLevelValue >= requiredLevelValue;
};