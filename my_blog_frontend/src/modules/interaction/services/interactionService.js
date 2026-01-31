/**
 * 互动服务
 * 对接后端 InteractionService API
 */

import { httpClient } from '../../../utils/httpClient';
import { API_ENDPOINTS } from '../../../config/apiConfig';

/**
 * 点赞帖子
 * @param {string} postId - 帖子 ID
 * @returns {Promise<Object>} 点赞结果
 */
export const likePost = async (postId) => {
  try {
    const result = await httpClient.post(`${API_ENDPOINTS.INTERACTION_SERVICE.LIKE_POST}/${postId}/like`);
    return result.data || null;
  } catch (error) {
    console.error('点赞帖子失败:', error);
    throw error;
  }
};

/**
 * 取消点赞帖子
 * @param {string} postId - 帖子 ID
 * @returns {Promise<Object>} 取消点赞结果
 */
export const unlikePost = async (postId) => {
  try {
    const result = await httpClient.delete(`${API_ENDPOINTS.INTERACTION_SERVICE.LIKE_POST}/${postId}/like`);
    return result.data || null;
  } catch (error) {
    console.error('取消点赞失败:', error);
    throw error;
  }
};

/**
 * 获取帖子点赞数
 * @param {string} postId - 帖子 ID
 * @returns {Promise<Object>} 点赞数据
 */
export const getPostLikes = async (postId) => {
  try {
    const result = await httpClient.get(`${API_ENDPOINTS.INTERACTION_SERVICE.GET_LIKES}/${postId}/likes`);
    return result.data || null;
  } catch (error) {
    console.error('获取帖子点赞数失败:', error);
    throw error;
  }
};

/**
 * 添加评论
 * @param {string} postId - 帖子 ID
 * @param {Object} commentData - 评论数据
 * @param {string} commentData.content - 评论内容
 * @param {string} commentData.parent_id - 父评论 ID（可选，用于回复）
 * @returns {Promise<Object>} 添加的评论
 */
export const addComment = async (postId, commentData) => {
  try {
    const result = await httpClient.post(`${API_ENDPOINTS.INTERACTION_SERVICE.CREATE_COMMENT}/${postId}/comments`, commentData);
    return result.data || null;
  } catch (error) {
    console.error('添加评论失败:', error);
    throw error;
  }
};

/**
 * 获取帖子评论列表
 * @param {string} postId - 帖子 ID
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise<Object>} 评论列表数据
 */
export const getPostComments = async (postId, params = {}) => {
  try {
    const { page = 1, page_size = 20 } = params;
    const queryParams = new URLSearchParams({ page, page_size });

    const result = await httpClient.get(`${API_ENDPOINTS.INTERACTION_SERVICE.GET_COMMENTS}/${postId}/comments?${queryParams.toString()}`);
    return {
      comments: result.data?.comments || [],
      total: result.data?.pagination?.total || 0,
      page: result.data?.pagination?.page || page,
      page_size: result.data?.pagination?.page_size || page_size,
      total_pages: result.data?.pagination?.total_pages || 0
    };
  } catch (error) {
    console.error('获取帖子评论失败:', error);
    throw error;
  }
};

/**
 * 删除评论
 * @param {string} commentId - 评论 ID
 * @returns {Promise<Object>} 删除结果
 */
export const deleteComment = async (commentId) => {
  try {
    const result = await httpClient.delete(`${API_ENDPOINTS.INTERACTION_SERVICE.DELETE_COMMENT}/${commentId}`);
    return result.data || null;
  } catch (error) {
    console.error('删除评论失败:', error);
    throw error;
  }
};

/**
 * 互动服务对象
 */
const interactionService = {
  likePost,
  unlikePost,
  getPostLikes,
  addComment,
  getPostComments,
  deleteComment
};

export default interactionService;