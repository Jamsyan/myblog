/**
 * 帖子服务
 * 对接后端 PostService API
 */

import { httpClient } from '../../../utils/httpClient';
import { API_ENDPOINTS } from '../../../config/apiConfig';

/**
 * 获取帖子列表
 * @param {number} userId - 用户 ID
 * @param {number} page - 页码
 * @param {number} limit - 每页数量
 * @returns {Promise<Object>} 帖子列表数据
 */
export const getPosts = async (userId, page = 1, limit = 10) => {
  try {
    const result = await httpClient.get(`${API_ENDPOINTS.POST_SERVICE.GET_POSTS}`, {
      headers: {
        'X-User-ID': userId
      }
    });

    return {
      posts: result.posts || [],
      total: result.total || 0,
      page: result.page || page,
      limit: result.limit || limit
    };
  } catch (error) {
    console.error('获取帖子列表失败:', error);
    throw error;
  }
};

/**
 * 根据类型获取帖子
 * @param {string} type - 帖子类型
 * @param {number} userId - 用户 ID
 * @param {number} page - 页码
 * @param {number} limit - 每页数量
 * @returns {Promise<Object>} 筛选后的帖子列表
 */
export const getPostsByType = async (type, userId, page = 1, limit = 10) => {
  try {
    const result = await httpClient.get(`${API_ENDPOINTS.POST_SERVICE.GET_POSTS}`, {
      headers: {
        'X-User-ID': userId
      }
    });

    const posts = result.posts || [];
    const filteredPosts = type === 'all' ? posts : posts.filter(post => post.type === type);

    return {
      posts: filteredPosts,
      total: filteredPosts.length,
      page: page,
      limit: limit
    };
  } catch (error) {
    console.error('获取帖子列表失败:', error);
    throw error;
  }
};

/**
 * 根据 ID 获取帖子详情
 * @param {string} postId - 帖子 ID
 * @param {number} userId - 用户 ID
 * @returns {Promise<Object>} 帖子详情
 */
export const getPostById = async (postId, userId) => {
  try {
    const result = await httpClient.get(`${API_ENDPOINTS.POST_SERVICE.GET_POST}/${postId}`, {
      headers: {
        'X-User-ID': userId
      }
    });

    return result.post || null;
  } catch (error) {
    console.error('获取帖子详情失败:', error);
    throw error;
  }
};

/**
 * 创建帖子
 * @param {Object} postData - 帖子数据
 * @param {number} postData.user_id - 用户 ID
 * @param {string} postData.title - 帖子标题
 * @param {string} postData.content - 帖子内容
 * @param {string} postData.type - 帖子类型
 * @param {string} postData.permission_level - 权限等级
 * @returns {Promise<Object>} 创建的帖子
 */
export const createPost = async (postData) => {
  try {
    const result = await httpClient.post(API_ENDPOINTS.POST_SERVICE.CREATE_POST, postData);
    return result.post || null;
  } catch (error) {
    console.error('创建帖子失败:', error);
    throw error;
  }
};

/**
 * 更新帖子
 * @param {string} postId - 帖子 ID
 * @param {Object} postData - 更新数据
 * @param {number} postData.user_id - 用户 ID
 * @param {string} postData.title - 帖子标题(可选)
 * @param {string} postData.content - 帖子内容(可选)
 * @param {string} postData.type - 帖子类型(可选)
 * @param {string} postData.permission_level - 权限等级(可选)
 * @returns {Promise<Object>} 更新后的帖子
 */
export const updatePost = async (postId, postData) => {
  try {
    const result = await httpClient.put(`${API_ENDPOINTS.POST_SERVICE.UPDATE_POST}/${postId}`, postData);
    return result.post || null;
  } catch (error) {
    console.error('更新帖子失败:', error);
    throw error;
  }
};

/**
 * 删除帖子
 * @param {string} postId - 帖子 ID
 * @param {number} userId - 用户 ID
 * @returns {Promise<Object>} 删除结果
 */
export const deletePost = async (postId, userId) => {
  try {
    const result = await httpClient.delete(`${API_ENDPOINTS.POST_SERVICE.DELETE_POST}/${postId}`, {
      body: { user_id: userId }
    });
    return result;
  } catch (error) {
    console.error('删除帖子失败:', error);
    throw error;
  }
};

/**
 * 获取帖子类型列表
 * @returns {Promise<Array>} 帖子类型列表
 */
export const getPostTypes = async () => {
  try {
    return [
      { id: 'all', name: '全部' },
      { id: 'technology', name: '技术' },
      { id: 'life', name: '生活' },
      { id: 'study', name: '学习' },
      { id: 'work', name: '工作' },
      { id: 'hobby', name: '爱好' }
    ];
  } catch (error) {
    console.error('获取帖子类型失败:', error);
    throw error;
  }
};

/**
 * 帖子服务对象
 */
const postService = {
  getPosts,
  getPostsByType,
  getPostById,
  createPost,
  updatePost,
  deletePost,
  getPostTypes
};

export default postService;