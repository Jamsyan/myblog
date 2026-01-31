/**
 * 用户资料服务
 * 对接后端 UserServer API
 */

import { httpClient } from '../../../utils/httpClient';
import { API_ENDPOINTS } from '../../../config/apiConfig';
import { getUserId } from '../../auth/services/authService';

/**
 * 获取用户资料
 * @param {string} userId - 用户 ID（可选，不传则获取当前用户）
 * @returns {Promise<Object>} 用户资料
 */
export const getUserProfile = async (userId = null) => {
  try {
    const targetUserId = userId || getUserId();
    if (!targetUserId) {
      throw new Error('用户 ID 不存在');
    }

    const result = await httpClient.get(`${API_ENDPOINTS.USER_SERVER.GET_USER}/${targetUserId}`);
    return result.data || null;
  } catch (error) {
    console.error('获取用户资料失败:', error);
    throw error;
  }
};

/**
 * 更新用户资料
 * @param {Object} profileData - 用户资料数据
 * @param {string} profileData.email - 邮箱（可选）
 * @param {string} profileData.bio - 个人简介（可选）
 * @param {string} profileData.avatar_url - 头像 URL（可选）
 * @returns {Promise<Object>} 更新后的用户资料
 */
export const updateUserProfile = async (profileData) => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('用户 ID 不存在');
    }

    const result = await httpClient.put(`${API_ENDPOINTS.USER_SERVER.UPDATE_USER}/${userId}`, profileData);
    return result.data || null;
  } catch (error) {
    console.error('更新用户资料失败:', error);
    throw error;
  }
};

/**
 * 上传头像
 * @param {File} file - 头像文件
 * @returns {Promise<Object>} 上传结果
 */
export const uploadAvatar = async (file) => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('用户 ID 不存在');
    }

    const formData = new FormData();
    formData.append('type', 'image');
    formData.append('name', file.name);
    formData.append('file_data', file);

    const result = await httpClient.post(`${API_ENDPOINTS.USER_SERVER.CREATE_ASSET}/${userId}/assets`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    return result.data || null;
  } catch (error) {
    console.error('上传头像失败:', error);
    throw error;
  }
};

/**
 * 修改密码
 * @param {Object} passwordData - 密码数据
 * @param {string} passwordData.old_password - 旧密码
 * @param {string} passwordData.new_password - 新密码
 * @returns {Promise<Object>} 修改结果
 */
export const changePassword = async (passwordData) => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('用户 ID 不存在');
    }

    const result = await httpClient.put(`${API_ENDPOINTS.USER_SERVER.UPDATE_USER}/${userId}`, passwordData);
    return result.data || null;
  } catch (error) {
    console.error('修改密码失败:', error);
    throw error;
  }
};

/**
 * 获取用户权限列表
 * @param {string} userId - 用户 ID（可选，不传则获取当前用户）
 * @returns {Promise<Object>} 用户权限数据
 */
export const getUserPermissions = async (userId = null) => {
  try {
    const targetUserId = userId || getUserId();
    if (!targetUserId) {
      throw new Error('用户 ID 不存在');
    }

    const result = await httpClient.get(`${API_ENDPOINTS.USER_SERVER.GET_PERMISSIONS}/${targetUserId}/permissions`);
    return result.data || null;
  } catch (error) {
    console.error('获取用户权限失败:', error);
    throw error;
  }
};

/**
 * 获取用户可访问页面
 * @param {string} userId - 用户 ID（可选，不传则获取当前用户）
 * @returns {Promise<Object>} 可访问页面列表
 */
export const getUserPages = async (userId = null) => {
  try {
    const targetUserId = userId || getUserId();
    if (!targetUserId) {
      throw new Error('用户 ID 不存在');
    }

    const result = await httpClient.get(`${API_ENDPOINTS.USER_SERVER.GET_PAGES}/${targetUserId}/pages`);
    return result.data || null;
  } catch (error) {
    console.error('获取用户可访问页面失败:', error);
    throw error;
  }
};

/**
 * 获取用户资产列表
 * @param {string} userId - 用户 ID（可选，不传则获取当前用户）
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise<Object>} 用户资产列表
 */
export const getUserAssets = async (userId = null, params = {}) => {
  try {
    const targetUserId = userId || getUserId();
    if (!targetUserId) {
      throw new Error('用户 ID 不存在');
    }

    const { page = 1, page_size = 20 } = params;
    const queryParams = new URLSearchParams({ page, page_size });

    const result = await httpClient.get(`${API_ENDPOINTS.USER_SERVER.GET_ASSETS}/${targetUserId}/assets?${queryParams.toString()}`);
    return result.data || null;
  } catch (error) {
    console.error('获取用户资产列表失败:', error);
    throw error;
  }
};

/**
 * 删除用户资产
 * @param {string} assetId - 资产 ID
 * @param {string} userId - 用户 ID（可选，不传则使用当前用户）
 * @returns {Promise<Object>} 删除结果
 */
export const deleteUserAsset = async (assetId, userId = null) => {
  try {
    const targetUserId = userId || getUserId();
    if (!targetUserId) {
      throw new Error('用户 ID 不存在');
    }

    const result = await httpClient.delete(`${API_ENDPOINTS.USER_SERVER.DELETE_ASSET}/${targetUserId}/assets/${assetId}`);
    return result.data || null;
  } catch (error) {
    console.error('删除用户资产失败:', error);
    throw error;
  }
};

/**
 * 用户资料服务对象
 */
const profileService = {
  getUserProfile,
  updateUserProfile,
  uploadAvatar,
  changePassword,
  getUserPermissions,
  getUserPages,
  getUserAssets,
  deleteUserAsset
};

export default profileService;