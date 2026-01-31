/**
 * 探索模块状态管理
 * 使用Vue 3的reactive API实现简单状态管理
 */

import { reactive, ref, computed } from 'vue';
import { postService } from '../services';

// 探索页面状态
const state = reactive({
  // 当前选中的帖子类型
  selectedType: 'all',
  // 帖子类型列表
  postTypes: [],
  // 帖子列表
  posts: [],
  // 当前选中的帖子
  selectedPost: null,
  // 加载状态
  loading: false,
  // 错误信息
  error: null,
  // 分页信息
  pagination: {
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0
  }
});

// 计算属性：根据选中类型过滤的帖子
const filteredPosts = computed(() => {
  if (state.selectedType === 'all') {
    return state.posts;
  }
  return state.posts.filter(post => post.tags && post.tags.includes(state.selectedType));
});

// 动作：设置选中的类型
const setSelectedType = (type) => {
  state.selectedType = type;
  state.selectedPost = null; // 切换类型时重置选中的帖子
};

// 动作：设置帖子列表
const setPosts = (posts) => {
  state.posts = posts;
};

// 动作：设置选中的帖子
const setSelectedPost = (post) => {
  state.selectedPost = post;
};

// 动作：设置加载状态
const setLoading = (loading) => {
  state.loading = loading;
};

// 动作：设置错误信息
const setError = (error) => {
  state.error = error;
};

// 动作：清除错误信息
const clearError = () => {
  state.error = null;
};

// 动作：设置帖子类型列表
const setPostTypes = (types) => {
  state.postTypes = types;
};

// 动作：设置分页信息
const setPagination = (pagination) => {
  state.pagination = pagination;
};

// 动作：获取帖子列表
const fetchPosts = async (params = {}) => {
  try {
    setLoading(true);
    clearError();
    const result = await postService.getPosts(params);
    setPosts(result.posts);
    setPagination({
      page: result.page,
      page_size: result.page_size,
      total: result.total,
      total_pages: result.total_pages
    });
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

// 动作：根据 ID 获取帖子详情
const fetchPostById = async (postId) => {
  try {
    setLoading(true);
    clearError();
    const result = await postService.getPostById(postId);
    setSelectedPost(result);
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

// 导出状态和方法
export const useExploreStore = () => {
  return {
    state,
    filteredPosts,
    selectedType: computed(() => state.selectedType),
    loading: computed(() => state.loading),
    error: computed(() => state.error),
    pagination: computed(() => state.pagination),
    setSelectedType,
    setPosts,
    setSelectedPost,
    setLoading,
    setError,
    clearError,
    setPostTypes,
    setPagination,
    fetchPosts,
    fetchPostById
  };
};

// 导出状态管理对象
export default {
  state,
  filteredPosts,
  setSelectedType,
  setPosts,
  setSelectedPost,
  setLoading,
  setError,
  clearError,
  setPostTypes,
  setPagination,
  fetchPosts,
  fetchPostById
};