<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getPostById } from '../services/postService';
import { useNavbarActions } from '../../../components/_base/navbarContext.js';
import { Icon } from '../../../components/_base/index.js';
import { getUserId } from '../../auth/services';

const route = useRoute();
const router = useRouter();
const { registerActions, setNavbarTitle, collapseNavbar } = useNavbarActions();

const post = ref(null);
const loading = ref(true);
const error = ref(null);

const loadPostDetail = async () => {
  const postId = route.params.id;
  const userId = getUserId();

  if (!userId) {
    error.value = '用户未登录,无法查看帖子';
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    const postData = await getPostById(postId, userId);

    if (postData) {
      post.value = postData;
    } else {
      error.value = '帖子不存在';
    }
  } catch (err) {
    error.value = '加载帖子失败';
    console.error('Failed to load post:', err);
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.push('/explore');
};

const handleShare = () => {
  if (navigator.share) {
    navigator.share({
      title: post.value.title,
      text: post.value.content.substring(0, 100),
      url: window.location.href
    });
  } else {
    navigator.clipboard.writeText(window.location.href);
    alert('链接已复制到剪贴板');
  }
};

const handleLike = () => {
  alert('点赞功能开发中...');
};

onMounted(async () => {
  await loadPostDetail();
  
  collapseNavbar();
  
  if (post.value) {
    setNavbarTitle(post.value.title);
  }
  
  registerActions([
    {
      icon: '←',
      text: '返回',
      label: '返回探索页面',
      onClick: goBack
    },
    {
      icon: '❤️',
      text: '点赞',
      label: '点赞这篇文章',
      onClick: handleLike
    },
    {
      icon: '📤',
      text: '分享',
      label: '分享这篇文章',
      onClick: handleShare
    }
  ]);
});
</script>

<template>
  <div class="post-detail-page">
    <div class="container">
      <!-- 加载状态 -->
      <div class="loading" v-if="loading">
        <p>加载中...</p>
      </div>

      <!-- 错误状态 -->
      <div class="error" v-else-if="error">
        <p>{{ error }}</p>
        <button class="back-button" @click="goBack">
          返回探索页面
        </button>
      </div>

      <!-- 帖子内容 -->
      <div v-else-if="post" class="post-content">
        <h1 class="post-title">{{ post.title }}</h1>
        <div class="post-meta">
          <span class="post-author">{{ post.author }}</span>
          <span class="post-date">{{ post.date }}</span>
        </div>
        <div class="post-body">
          <p v-for="(paragraph, index) in post.content.split('\n')" :key="index">
            {{ paragraph }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-detail-page {
  min-height: 100vh;
  padding: 2rem 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--border-radius-md);
  background-color: var(--card-background);
  backdrop-filter: blur(15px);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9375rem;
}

.back-button:hover {
  background-color: var(--hover-background);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.loading,
.error {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 4rem 0;
  text-align: center;
  color: var(--text-secondary);
}

.error {
  gap: 1.5rem;
  color: var(--error-color, #e53e3e);
}

.post-content {
  background-color: var(--card-background);
  backdrop-filter: blur(15px);
  border-radius: var(--border-radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-card);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.post-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  line-height: 1.3;
}

.post-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  font-size: 0.9375rem;
  color: var(--text-muted);
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.post-body {
  font-size: 1rem;
  line-height: 1.8;
  color: var(--text-primary);
}

.post-body p {
  margin-bottom: 1.5rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-detail-page {
    padding: 1.5rem 0;
  }

  .container {
    padding: 0 1rem;
  }

  .post-content {
    padding: 1.5rem;
  }

  .post-title {
    font-size: 1.75rem;
  }

  .back-button {
    margin-bottom: 1.5rem;
    padding: 0.625rem 1.25rem;
  }
}

/* 深色主题适配 */
.dark-theme .post-content {
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.dark-theme .back-button {
  border-color: rgba(255, 255, 255, 0.1);
}
</style>