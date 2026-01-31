<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentUser, logout } from '../../auth/services/authService';
import { getPosts, deletePost, publishPost, retractPost } from '../services';
import { useProfileStore } from '../store';
import { useNavbarActions } from '../../../components/_base/navbarContext.js';
import { Icon } from '../../../components/_base/index.js';
import PostEditor from './PostEditor.vue';
import ThemeSettings from './ThemeSettings.vue';

const router = useRouter();
const { state, setActiveTab, setPosts, setUser } = useProfileStore();
const { registerActions, setNavbarTitle, collapseNavbar } = useNavbarActions();

const user = ref(null);
const editingPost = ref(null);
const showEditor = ref(false);

const loadPosts = async () => {
  try {
    const posts = await getPosts();
    setPosts(posts);
  } catch (error) {
    console.error('Failed to load posts:', error);
  }
};

const handleLogout = () => {
  logout();
  router.push('/login');
};

const handleEditPost = (post) => {
  editingPost.value = post;
  showEditor.value = true;
};

const handleCreatePost = () => {
  editingPost.value = null;
  showEditor.value = true;
};

const handleDeletePost = async (postId) => {
  if (confirm('确定要删除这篇帖子吗？')) {
    try {
      await deletePost(postId);
      await loadPosts();
    } catch (error) {
      console.error('Failed to delete post:', error);
    }
  }
};

const handlePublishPost = async (postId) => {
  try {
    await publishPost(postId);
    await loadPosts();
  } catch (error) {
    console.error('Failed to publish post:', error);
  }
};

const handleRetractPost = async (postId) => {
  if (confirm('确定要撤回这篇帖子吗？')) {
    try {
      await retractPost(postId);
      await loadPosts();
    } catch (error) {
      console.error('Failed to retract post:', error);
    }
  }
};

const handleEditorSave = async () => {
  showEditor.value = false;
  editingPost.value = null;
  await loadPosts();
};

const handleEditorCancel = () => {
  showEditor.value = false;
  editingPost.value = null;
};

onMounted(async () => {
  user.value = getCurrentUser();
  setUser(user.value);
  await loadPosts();
  
  collapseNavbar();
  setNavbarTitle('个人中心');
  
  registerActions([
    {
      icon: 'Edit',
      text: '编辑资料',
      label: '编辑个人资料',
      className: 'primary',
      onClick: () => {
        setActiveTab('settings');
      }
    },
    {
      icon: 'Palette',
      text: '主题设置',
      label: '更改主题',
      onClick: () => {
        setActiveTab('theme');
      }
    }
  ]);
});
</script>

<template>
  <div class="profile-page">
    <div v-if="showEditor" class="editor-overlay">
      <PostEditor
        :post="editingPost"
        @save="handleEditorSave"
        @cancel="handleEditorCancel"
      />
    </div>

    <aside class="profile-sidebar">
      <div class="sidebar-header">
        <div class="user-info">
          <div class="user-avatar">
            <img
              :src="user?.avatar || 'https://via.placeholder.com/48'"
              alt="User avatar"
              class="avatar-img"
            >
          </div>
          <div class="user-details">
            <h3 class="user-name">{{ user?.username || '用户' }}</h3>
            <p class="user-email">{{ user?.email || 'user@example.com' }}</p>
          </div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <button
          @click="setActiveTab('posts')"
          :class="['nav-item', { active: state.activeTab === 'posts' }]"
        >
          <Icon name="FileText" :size="18" />
          <span>帖子管理</span>
        </button>

        <button
          @click="setActiveTab('profile')"
          :class="['nav-item', { active: state.activeTab === 'profile' }]"
        >
          <Icon name="User" :size="18" />
          <span>个人资料</span>
        </button>

        <button
          @click="setActiveTab('settings')"
          :class="['nav-item', { active: state.activeTab === 'settings' }]"
        >
          <Icon name="Settings" :size="18" />
          <span>主题设置</span>
        </button>

        <button
          @click="setActiveTab('analytics')"
          :class="['nav-item', { active: state.activeTab === 'analytics' }]"
        >
          <Icon name="BarChart" :size="18" />
          <span>数据分析</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <button @click="handleLogout" class="logout-btn">
          <Icon name="LogOut" :size="16" />
          <span>登出</span>
        </button>
      </div>
    </aside>

    <main class="profile-content">
      <div v-if="state.activeTab === 'posts'" class="tab-content">
        <div class="content-header">
          <h1>帖子管理</h1>
          <button class="primary-btn" @click="handleCreatePost">
            <Icon name="Plus" :size="16" />
            创建新帖子
          </button>
        </div>

        <div class="posts-list">
          <div class="posts-header">
            <div class="header-item">标题</div>
            <div class="header-item">状态</div>
            <div class="header-item">创建时间</div>
            <div class="header-item">浏览量</div>
            <div class="header-item">操作</div>
          </div>

          <div v-for="post in state.posts" :key="post.id" class="post-item">
            <div class="post-title">{{ post.title }}</div>
            <div class="post-status">
              <span :class="['status-badge', post.status]">
                {{ post.status === 'published' ? '已发布' : '草稿' }}
              </span>
            </div>
            <div class="post-date">{{ post.createdAt }}</div>
            <div class="post-views">{{ post.views }}</div>
            <div class="post-actions">
              <button class="action-btn edit" @click="handleEditPost(post)">编辑</button>
              <button
                v-if="post.status === 'draft'"
                class="action-btn publish"
                @click="handlePublishPost(post.id)"
              >
                发布
              </button>
              <button
                v-if="post.status === 'published'"
                class="action-btn retract"
                @click="handleRetractPost(post.id)"
              >
                撤回
              </button>
              <button class="action-btn delete" @click="handleDeletePost(post.id)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="state.activeTab === 'profile'" class="tab-content">
        <div class="content-header">
          <h1>个人资料</h1>
        </div>

        <div class="profile-form">
          <div class="form-group">
            <label>用户名</label>
            <input type="text" :value="user?.username || ''" class="form-input">
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input type="email" :value="user?.email || ''" class="form-input">
          </div>
          <div class="form-group">
            <label>头像</label>
            <div class="avatar-upload">
              <img
                :src="user?.avatar || 'https://via.placeholder.com/80'"
                alt="User avatar"
                class="preview-avatar"
              >
              <button class="upload-btn">更换头像</button>
            </div>
          </div>
          <button class="primary-btn">保存修改</button>
        </div>
      </div>

      <div v-if="state.activeTab === 'settings'" class="tab-content">
        <ThemeSettings />
      </div>

      <div v-if="state.activeTab === 'analytics'" class="tab-content">
        <div class="content-header">
          <h1>数据分析</h1>
        </div>

        <div class="analytics-dashboard">
          <div class="analytics-card">
            <h3>总浏览量</h3>
            <p class="analytics-value">1,245</p>
          </div>
          <div class="analytics-card">
            <h3>总帖子数</h3>
            <p class="analytics-value">{{ state.posts.length }}</p>
          </div>
          <div class="analytics-card">
            <h3>总评论数</h3>
            <p class="analytics-value">89</p>
          </div>
          <div class="analytics-card">
            <h3>总点赞数</h3>
            <p class="analytics-value">234</p>
          </div>
        </div>

        <div class="analytics-chart">
          <h3>浏览量趋势</h3>
          <div class="chart-placeholder">
            <div class="chart-bar"></div>
            <div class="chart-bar"></div>
            <div class="chart-bar"></div>
            <div class="chart-bar"></div>
            <div class="chart-bar"></div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.profile-page {
  display: flex;
  min-height: 100vh;
  background: var(--background-primary);
  color: var(--text-primary);
}

.editor-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.profile-sidebar {
  width: 280px;
  background: var(--card-background);
  backdrop-filter: blur(10px);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--background-primary);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: var(--text-primary);
}

.user-email {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 14px 24px;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-primary);
  border-radius: 0 25px 25px 0;
}

.nav-item:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--primary-color);
}

.nav-item.active {
  background: var(--primary-color);
  color: white;
}

.sidebar-footer {
  padding: 24px;
  border-top: 1px solid var(--border-color);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 20px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-secondary);
}

.logout-btn:hover {
  border-color: var(--error-color);
  color: var(--error-color);
  background: rgba(239, 68, 68, 0.05);
}

.profile-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.content-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.primary-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.primary-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

.posts-list {
  background: var(--card-background);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.posts-header {
  display: grid;
  grid-template-columns: 1fr 120px 150px 100px 200px;
  padding: 16px 24px;
  background: var(--background-primary);
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  color: var(--text-primary);
}

.post-item {
  display: grid;
  grid-template-columns: 1fr 120px 150px 100px 200px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  align-items: center;
}

.post-item:last-child {
  border-bottom: none;
}

.post-item:hover {
  background: rgba(0, 0, 0, 0.02);
}

.post-title {
  font-weight: 500;
  color: var(--text-primary);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.published {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.draft {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.post-date {
  color: var(--text-secondary);
}

.post-views {
  color: var(--text-secondary);
}

.post-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.action-btn.edit {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.action-btn.edit:hover {
  background: #3b82f6;
  color: white;
}

.action-btn.publish {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.action-btn.publish:hover {
  background: #10b981;
  color: white;
}

.action-btn.retract {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.action-btn.retract:hover {
  background: #f59e0b;
  color: white;
}

.action-btn.delete {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.action-btn.delete:hover {
  background: #ef4444;
  color: white;
}

.profile-form {
  background: var(--card-background);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 32px;
  box-shadow: var(--shadow-md);
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--background-primary);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.preview-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border-color);
}

.upload-btn {
  padding: 10px 20px;
  background: var(--background-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-primary);
}

.upload-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.analytics-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.analytics-card {
  background: var(--card-background);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
}

.analytics-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.analytics-card h3 {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.analytics-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.analytics-chart {
  background: var(--card-background);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-md);
}

.analytics-chart h3 {
  font-size: 1.2rem;
  color: var(--text-primary);
  margin: 0 0 24px 0;
}

.chart-placeholder {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  height: 200px;
  padding: 24px 0;
}

.chart-bar {
  flex: 1;
  background: var(--primary-color);
  border-radius: 4px 4px 0 0;
  animation: barGrow 1s ease-out;
}

.chart-bar:nth-child(1) {
  height: 60%;
}

.chart-bar:nth-child(2) {
  height: 80%;
}

.chart-bar:nth-child(3) {
  height: 40%;
}

.chart-bar:nth-child(4) {
  height: 90%;
}

.chart-bar:nth-child(5) {
  height: 70%;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes barGrow {
  from {
    height: 0;
  }
  to {
    height: var(--height);
  }
}

@media (max-width: 1024px) {
  .profile-sidebar {
    width: 240px;
  }

  .profile-content {
    padding: 24px;
  }

  .posts-header,
  .post-item {
    grid-template-columns: 1fr 100px 120px 80px 180px;
  }
}

@media (max-width: 768px) {
  .profile-page {
    flex-direction: column;
  }

  .profile-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
    padding: 16px;
  }

  .sidebar-nav {
    display: flex;
    overflow-x: auto;
    gap: 8px;
    padding: 16px 0;
  }

  .nav-item {
    white-space: nowrap;
    border-radius: 8px;
    padding: 10px 16px;
  }

  .posts-header,
  .post-item {
    grid-template-columns: 1fr;
    gap: 8px;
    text-align: left;
  }

  .header-item {
    display: none;
  }

  .analytics-dashboard {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>