import { ref, computed } from 'vue';
import { interactionService } from '../services';

const state = ref({
  likes: {},
  comments: {},
  loading: false,
  error: null
});

export function useInteractionStore() {
  const loading = computed(() => state.value.loading);
  const error = computed(() => state.value.error);

  const getPostLikes = (postId) => {
    return state.value.likes[postId] || { like_count: 0, liked: false };
  };

  const getPostComments = (postId) => {
    return state.value.comments[postId] || { comments: [], total: 0, page: 1, page_size: 20, total_pages: 0 };
  };

  const setPostLikes = (postId, likesData) => {
    state.value.likes[postId] = likesData;
  };

  const setPostComments = (postId, commentsData) => {
    state.value.comments[postId] = commentsData;
  };

  const setLoading = (isLoading) => {
    state.value.loading = isLoading;
  };

  const setError = (errorMessage) => {
    state.value.error = errorMessage;
  };

  const clearError = () => {
    state.value.error = null;
  };

  const fetchPostLikes = async (postId) => {
    try {
      setLoading(true);
      clearError();
      const result = await interactionService.getPostLikes(postId);
      setPostLikes(postId, result);
      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const likePost = async (postId) => {
    try {
      setLoading(true);
      clearError();
      const result = await interactionService.likePost(postId);
      setPostLikes(postId, result);
      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const unlikePost = async (postId) => {
    try {
      setLoading(true);
      clearError();
      const result = await interactionService.unlikePost(postId);
      setPostLikes(postId, result);
      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const fetchPostComments = async (postId, params = {}) => {
    try {
      setLoading(true);
      clearError();
      const result = await interactionService.getPostComments(postId, params);
      setPostComments(postId, result);
      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const addComment = async (postId, commentData) => {
    try {
      setLoading(true);
      clearError();
      const result = await interactionService.addComment(postId, commentData);
      
      const currentComments = getPostComments(postId);
      setPostComments(postId, {
        ...currentComments,
        comments: [result, ...currentComments.comments],
        total: currentComments.total + 1
      });
      
      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteComment = async (commentId, postId) => {
    try {
      setLoading(true);
      clearError();
      await interactionService.deleteComment(commentId);
      
      const currentComments = getPostComments(postId);
      setPostComments(postId, {
        ...currentComments,
        comments: currentComments.comments.filter(c => c.comment_id !== commentId),
        total: currentComments.total - 1
      });
      
      return { success: true };
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    getPostLikes,
    getPostComments,
    fetchPostLikes,
    likePost,
    unlikePost,
    fetchPostComments,
    addComment,
    deleteComment,
    clearError
  };
}

export default useInteractionStore;