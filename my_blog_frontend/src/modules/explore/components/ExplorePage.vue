<script setup>
// 导入探索模块组件
import { ExploreSidebar, PostList } from './index.js';
// 导入状态管理
import { useExploreStore } from '../store';
// 导入服务
import { getPosts } from '../services';
// 导入认证服务
import { getUserId } from '../../auth/services';

// 使用状态管理
const { state, filteredPosts, setSelectedType, setPosts, setLoading } = useExploreStore();

// 初始化加载帖子数据
const loadPosts = async () => {
  setLoading(true);
  try {
    const userId = getUserId();
    if (!userId) {
      console.warn('用户未登录,无法加载帖子');
      setPosts([]);
      return;
    }
    const result = await getPosts(userId, 1, 20);
    setPosts(result.posts || []);
  } catch (error) {
    console.error('Failed to load posts:', error);
    setPosts([]);
  } finally {
    setLoading(false);
  }
};

// 组件挂载时加载数据
loadPosts();

// 处理类型变更
const handleTypeChange = (type) => {
  setSelectedType(type);
};
</script>

<template>
  <!-- 探索页面 -->
  <div class="explore-page">
    <!-- 左侧侧边栏 -->
    <ExploreSidebar @type-change="handleTypeChange" />
    
    <!-- 右侧内容区域 -->
    <div class="explore-content">
      <!-- 帖子列表 -->
      <PostList 
        :posts="filteredPosts" 
        :loading="state.loading"
      />
    </div>
  </div>
</template>

<style scoped>
/* 探索页面样式 */
.explore-page {
  display: flex;
  height: 100%;
  gap: 2rem;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* 左侧侧边栏 */
.explore-sidebar {
  width: 280px;
  background: var(--card-background);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
  position: sticky;
  top: 2rem;
  height: fit-content;
  max-height: calc(100vh - 4rem);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 右侧内容区域 */
.explore-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
  padding-right: 0.5rem; /* 为滚动条留出空间 */
}

/* 自定义滚动条样式 */
.explore-content::-webkit-scrollbar {
  width: 6px;
}

.explore-content::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.explore-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.explore-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 帖子列表 */
.post-list {
  background: var(--card-background);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
  overflow-y: auto;
  min-height: 400px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 深色主题适配 */
.dark-theme .explore-sidebar,
.dark-theme .post-list {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .explore-page {
    flex-direction: column;
    padding: 1.5rem;
    gap: 1.5rem;
  }

  .explore-sidebar {
    width: 100%;
    position: static;
    margin-bottom: 0;
    max-height: none;
  }

  .post-list {
    padding: 1.5rem;
    min-height: 300px;
  }
}
</style>