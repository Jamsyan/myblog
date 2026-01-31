import { ref, computed } from 'vue';
import { postService } from '../services';
import { profileService } from '../services';
import { getUserId } from '../../auth/services/authService';

const state = ref({
  activeTab: 'posts',
  posts: [],
  user: null,
  loading: false,
  error: null,
  theme: localStorage.getItem('theme') || 'china-red',
  pagination: {
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0
  }
});

const themes = [
  { id: 'china-red', name: '中国红' },
  { id: 'danqing-blue', name: '丹青蓝' },
  { id: 'fenxia-purple', name: '粉霞紫' }
];

const setActiveTab = (tab) => {
  state.value.activeTab = tab;
};

const setPosts = (posts) => {
  state.value.posts = posts;
};

const setUser = (user) => {
  state.value.user = user;
};

const setLoading = (loading) => {
  state.value.loading = loading;
};

const setError = (error) => {
  state.value.error = error;
};

const clearError = () => {
  state.value.error = null;
};

const setTheme = (theme) => {
  state.value.theme = theme;
  localStorage.setItem('theme', theme);
  document.body.className = `theme-${theme}`;
};

const setPagination = (pagination) => {
  state.value.pagination = pagination;
};

const filteredPosts = computed(() => {
  return state.value.posts;
});

const fetchPosts = async (params = {}) => {
  try {
    setLoading(true);
    clearError();
    const userId = getUserId();
    const result = await postService.getPosts({ ...params, author_id: userId });
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

const createPost = async (postData) => {
  try {
    setLoading(true);
    clearError();
    const result = await postService.createPost(postData);
    setPosts([result, ...state.value.posts]);
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

const updatePost = async (postId, postData) => {
  try {
    setLoading(true);
    clearError();
    const result = await postService.updatePost(postId, postData);
    const index = state.value.posts.findIndex(post => post.post_id === postId);
    if (index !== -1) {
      state.value.posts[index] = result;
    }
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

const deletePost = async (postId) => {
  try {
    setLoading(true);
    clearError();
    await postService.deletePost(postId);
    setPosts(state.value.posts.filter(post => post.post_id !== postId));
    return { success: true };
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

const publishPost = async (postId) => {
  try {
    setLoading(true);
    clearError();
    const result = await postService.publishPost(postId);
    const index = state.value.posts.findIndex(post => post.post_id === postId);
    if (index !== -1) {
      state.value.posts[index] = result;
    }
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

const retractPost = async (postId) => {
  try {
    setLoading(true);
    clearError();
    const result = await postService.retractPost(postId);
    const index = state.value.posts.findIndex(post => post.post_id === postId);
    if (index !== -1) {
      state.value.posts[index] = result;
    }
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

const fetchUserProfile = async (userId = null) => {
  try {
    setLoading(true);
    clearError();
    const result = await profileService.getUserProfile(userId);
    setUser(result);
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

const updateUserProfile = async (profileData) => {
  try {
    setLoading(true);
    clearError();
    const result = await profileService.updateUserProfile(profileData);
    setUser(result);
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

const uploadAvatar = async (file) => {
  try {
    setLoading(true);
    clearError();
    const result = await profileService.uploadAvatar(file);
    if (state.value.user) {
      state.value.user.avatar_url = result.url;
    }
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

const changePassword = async (passwordData) => {
  try {
    setLoading(true);
    clearError();
    const result = await profileService.changePassword(passwordData);
    return result;
  } catch (error) {
    setError(error.message);
    throw error;
  } finally {
    setLoading(false);
  }
};

export const useProfileStore = () => {
  return {
    state,
    themes,
    filteredPosts,
    activeTab: computed(() => state.value.activeTab),
    loading: computed(() => state.value.loading),
    error: computed(() => state.value.error),
    pagination: computed(() => state.value.pagination),
    setActiveTab,
    setPosts,
    setUser,
    setLoading,
    setError,
    clearError,
    setTheme,
    setPagination,
    fetchPosts,
    createPost,
    updatePost,
    deletePost,
    publishPost,
    retractPost,
    fetchUserProfile,
    updateUserProfile,
    uploadAvatar,
    changePassword
  };
};