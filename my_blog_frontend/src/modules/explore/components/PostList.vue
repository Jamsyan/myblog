<script setup>
import { defineProps } from 'vue';
import { useRouter } from 'vue-router';

// 使用路由
const router = useRouter();

// 接收帖子数据
const props = defineProps({
  posts: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
});

// 选择帖子，跳转到详情页面
const handlePostSelect = (post) => {
  router.push(`/explore/post/${post.id}`);
};
</script>

<template>
  <div class="post-list">
    <h2>帖子列表</h2>
    
    <!-- 加载状态 -->
    <div class="loading" v-if="loading">
      <p>加载中...</p>
    </div>
    
    <!-- 帖子卡片列表 -->
    <div class="post-cards">
      <div
        v-for="post in posts"
        :key="post.id"
        class="post-card"
        @click="handlePostSelect(post)"
      >
        <h3 class="post-title">{{ post.title }}</h3>
        <p class="post-summary">{{ post.summary }}</p>
        <div class="post-meta">
          <span class="post-author">{{ post.author }}</span>
          <span class="post-date">{{ post.date }}</span>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-if="!loading && posts.length === 0">
      <p>暂无帖子</p>
    </div>
  </div>
</template>

<style scoped>
.post-list {
  flex: 1;
  min-width: 0;
}

.post-list h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.post-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.post-card {
  background-color: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
  border-color: var(--primary-color);
  background-color: rgba(255, 255, 255, 0.9);
}

/* 深色主题适配 */
.dark-theme .post-card {
  background-color: rgba(30, 30, 30, 0.75);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dark-theme .post-card:hover {
  background-color: rgba(40, 40, 40, 0.9);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  border-color: var(--primary-color);
}

.post-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-primary);
  line-height: 1.4;
}

.post-summary {
  font-size: 0.9375rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem;
  background-color: var(--card-background);
  border-radius: var(--border-radius-lg);
  color: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .post-cards {
    grid-template-columns: 1fr;
  }
  
  .post-list h2 {
    font-size: 1.25rem;
  }
}
</style>