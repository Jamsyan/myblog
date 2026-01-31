/**
 * 帖子服务
 * 对接后端 PostService API
 */

import { httpClient } from '../../../utils/httpClient';
import { API_ENDPOINTS } from '../../../config/apiConfig';

/**
 * 获取帖子列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.author_id - 作者ID（可选）
 * @param {string} params.tag - 标签筛选（可选）
 * @param {string} params.visibility - 可见性筛选（可选）
 * @param {string} params.sort_by - 排序字段（可选）
 * @param {string} params.sort_order - 排序顺序（可选）
 * @returns {Promise<Object>} 帖子列表数据
 */
export const getPosts = async (params = {}) => {
  try {
    const {
      page = 1,
      page_size = 20,
      author_id,
      tag,
      visibility = 'public',
      sort_by = 'created_at',
      sort_order = 'desc'
    } = params;

    const queryParams = new URLSearchParams({
      page,
      page_size,
      visibility,
      sort_by,
      sort_order
    });

    if (author_id) queryParams.append('author_id', author_id);
    if (tag) queryParams.append('tag', tag);

    const result = await httpClient.get(`${API_ENDPOINTS.POST_SERVICE.GET_POSTS}?${queryParams.toString()}`);

    return {
      posts: result.data?.posts || [],
      total: result.data?.pagination?.total || 0,
      page: result.data?.pagination?.page || page,
      page_size: result.data?.pagination?.page_size || page_size,
      total_pages: result.data?.pagination?.total_pages || 0
    };
  } catch (error) {
    console.error('获取帖子列表失败:', error);
    throw error;
  }
};

/**
 * 根据 ID 获取帖子详情
 * @param {string} postId - 帖子 ID
 * @returns {Promise<Object>} 帖子详情
 */
export const getPostById = async (postId) => {
  try {
    const result = await httpClient.get(`${API_ENDPOINTS.POST_SERVICE.GET_POST}/${postId}`);
    return result.data || null;
  } catch (error) {
    console.error('获取帖子详情失败:', error);
    throw error;
  }
};

/**
 * 创建帖子
 * @param {Object} postData - 帖子数据
 * @param {string} postData.title - 帖子标题
 * @param {string} postData.content - 帖子内容
 * @param {string} postData.summary - 帖子摘要（可选）
 * @param {Array} postData.tags - 标签列表（可选）
 * @param {string} postData.visibility - 可见性（可选）
 * @returns {Promise<Object>} 创建的帖子
 */
export const createPost = async (postData) => {
  try {
    const result = await httpClient.post(API_ENDPOINTS.POST_SERVICE.CREATE_POST, postData);
    return result.data || null;
  } catch (error) {
    console.error('创建帖子失败:', error);
    throw error;
  }
};

/**
 * 更新帖子
 * @param {string} postId - 帖子 ID
 * @param {Object} postData - 更新数据
 * @param {string} postData.title - 帖子标题（可选）
 * @param {string} postData.content - 帖子内容（可选）
 * @param {string} postData.summary - 帖子摘要（可选）
 * @param {Array} postData.tags - 标签列表（可选）
 * @param {string} postData.visibility - 可见性（可选）
 * @returns {Promise<Object>} 更新后的帖子
 */
export const updatePost = async (postId, postData) => {
  try {
    const result = await httpClient.put(`${API_ENDPOINTS.POST_SERVICE.UPDATE_POST}/${postId}`, postData);
    return result.data || null;
  } catch (error) {
    console.error('更新帖子失败:', error);
    throw error;
  }
};

/**
 * 删除帖子
 * @param {string} postId - 帖子 ID
 * @returns {Promise<Object>} 删除结果
 */
export const deletePost = async (postId) => {
  try {
    const result = await httpClient.delete(`${API_ENDPOINTS.POST_SERVICE.DELETE_POST}/${postId}`);
    return result.data || null;
  } catch (error) {
    console.error('删除帖子失败:', error);
    throw error;
  }
};

/**
 * 发布帖子（将帖子状态设为公开）
 * @param {string} postId - 帖子 ID
 * @returns {Promise<Object>} 发布结果
 */
export const publishPost = async (postId) => {
  try {
    const result = await httpClient.put(`${API_ENDPOINTS.POST_SERVICE.UPDATE_POST}/${postId}`, {
      visibility: 'public'
    });
    return result.data || null;
  } catch (error) {
    console.error('发布帖子失败:', error);
    throw error;
  }
};

/**
 * 撤回帖子（将帖子状态设为私有）
 * @param {string} postId - 帖子 ID
 * @returns {Promise<Object>} 撤回结果
 */
export const retractPost = async (postId) => {
  try {
    const result = await httpClient.put(`${API_ENDPOINTS.POST_SERVICE.UPDATE_POST}/${postId}`, {
      visibility: 'private'
    });
    return result.data || null;
  } catch (error) {
    console.error('撤回帖子失败:', error);
    throw error;
  }
};

/**
 * 帖子服务对象
 */
const postService = {
  getPosts,
  getPostById,
  createPost,
  updatePost,
  deletePost,
  publishPost,
  retractPost
};

export default postService;