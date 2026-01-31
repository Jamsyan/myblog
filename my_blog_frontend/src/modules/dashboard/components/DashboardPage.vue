<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentUser, logout } from '../../auth/services/authService';
import { Icon } from '../../../components/_base/index.js';

const router = useRouter();
const user = ref(null);
const activeTab = ref('posts');

// 模拟帖子数据
const posts = ref([
  {
    id: 1,
    title: '我的第一篇博客',
    status: 'published',
    createdAt: '2024-01-20',
    views: 120
  },
  {
    id: 2,
    title: '前端开发技巧分享',
    status: 'draft',
    createdAt: '2024-01-19',
    views: 0
  },
  {
    id: 3,
    title: 'Vue 3 新特性探索',
    status: 'published',
    createdAt: '2024-01-18',
    views: 85
  }
]);

// 切换标签
const switchTab = (tab) => {
  activeTab.value = tab;
};

// 处理登出
const handleLogout = () => {
  logout();
  router.push('/login');
};

// 初始化用户信息
const initUserInfo = () => {
  user.value = getCurrentUser();
};

// 组件挂载时初始化
onMounted(() => {
  initUserInfo();
});
</script>

<template>
  <div class="dashboard">
    <!-- 侧边栏 -->
    <aside class="dashboard-sidebar">
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
          @click="switchTab('posts')"
          :class="['nav-item', { active: activeTab === 'posts' }]"
        >
          <Icon name="FileText" :size="18" />
          <span>帖子管理</span>
        </button>
        
        <button 
          @click="switchTab('profile')"
          :class="['nav-item', { active: activeTab === 'profile' }]"
        >
          <Icon name="User" :size="18" />
          <span>个人资料</span>
        </button>
        
        <button 
          @click="switchTab('settings')"
          :class="['nav-item', { active: activeTab === 'settings' }]"
        >
          <Icon name="Settings" :size="18" />
          <span>账户设置</span>
        </button>
        
        <button 
          @click="switchTab('analytics')"
          :class="['nav-item', { active: activeTab === 'analytics' }]"
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
    
    <!-- 主内容区 -->
    <main class="dashboard-content">
      <!-- 帖子管理 -->
      <div v-if="activeTab === 'posts'" class="tab-content">
        <div class="content-header">
          <h1>帖子管理</h1>
          <button class="primary-btn">创建新帖子</button>
        </div>
        
        <div class="posts-list">
          <div class="posts-header">
            <div class="header-item">标题</div>
            <div class="header-item">状态</div>
            <div class="header-item">创建时间</div>
            <div class="header-item">浏览量</div>
            <div class="header-item">操作</div>
          </div>
          
          <div v-for="post in posts" :key="post.id" class="post-item">
            <div class="post-title">{{ post.title }}</div>
            <div class="post-status">
              <span :class="['status-badge', post.status]">
                {{ post.status === 'published' ? '已发布' : '草稿' }}
              </span>
            </div>
            <div class="post-date">{{ post.createdAt }}</div>
            <div class="post-views">{{ post.views }}</div>
            <div class="post-actions">
              <button class="action-btn edit">编辑</button>
              <button class="action-btn delete">删除</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 个人资料 -->
      <div v-if="activeTab === 'profile'" class="tab-content">
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
      
      <!-- 账户设置 -->
      <div v-if="activeTab === 'settings'" class="tab-content">
        <div class="content-header">
          <h1>账户设置</h1>
        </div>
        
        <div class="settings-form">
          <div class="form-group">
            <label>密码</label>
            <input type="password" placeholder="输入新密码" class="form-input">
          </div>
          <div class="form-group">
            <label>确认密码</label>
            <input type="password" placeholder="确认新密码" class="form-input">
          </div>
          <div class="form-group">
            <label class="toggle-label">
              <input type="checkbox" class="toggle-input">
              <span class="toggle-slider"></span>
              启用两步验证
            </label>
          </div>
          <button class="primary-btn">更新设置</button>
        </div>
      </div>
      
      <!-- 数据分析 -->
      <div v-if="activeTab === 'analytics'" class="tab-content">
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
            <p class="analytics-value">12</p>
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
            <!-- 图表占位符 -->
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
/* 工作台容器 */
.dashboard {
  display: flex;
  min-height: 100vh;
  background: var(--background-primary);
  color: var(--text-primary);
}

/* 侧边栏 */
.dashboard-sidebar {
  width: 280px;
  background: var(--background-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.dark-theme .dashboard-sidebar {
  background: var(--background-tertiary);
  border-right-color: var(--border-color-dark);
}

/* 侧边栏头部 */
.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
}

.dark-theme .sidebar-header {
  border-bottom-color: var(--border-color-dark);
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

/* 侧边栏导航 */
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

.dark-theme .nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background: var(--primary-color);
  color: white;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 24px;
  border-top: 1px solid var(--border-color);
}

.dark-theme .sidebar-footer {
  border-top-color: var(--border-color-dark);
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

/* 主内容区 */
.dashboard-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

/* 内容头部 */
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

/* 按钮样式 */
.primary-btn {
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

/* 标签内容 */
.tab-content {
  animation: fadeIn 0.3s ease;
}

/* 帖子列表 */
.posts-list {
  background: var(--background-secondary);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.dark-theme .posts-list {
  background: var(--background-tertiary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.posts-header {
  display: grid;
  grid-template-columns: 1fr 120px 150px 100px 120px;
  padding: 16px 24px;
  background: var(--background-primary);
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  color: var(--text-primary);
}

.dark-theme .posts-header {
  background: var(--background-secondary);
  border-bottom-color: var(--border-color-dark);
}

.post-item {
  display: grid;
  grid-template-columns: 1fr 120px 150px 100px 120px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  align-items: center;
}

.dark-theme .post-item {
  border-bottom-color: var(--border-color-dark);
}

.post-item:last-child {
  border-bottom: none;
}

.post-item:hover {
  background: rgba(0, 0, 0, 0.02);
}

.dark-theme .post-item:hover {
  background: rgba(255, 255, 255, 0.02);
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

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  margin-right: 8px;
}

.action-btn.edit {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.action-btn.edit:hover {
  background: #3b82f6;
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

/* 表单样式 */
.profile-form,
.settings-form {
  background: var(--background-secondary);
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.dark-theme .profile-form,
.dark-theme .settings-form {
  background: var(--background-tertiary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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

.dark-theme .form-input {
  background: var(--background-secondary);
  border-color: var(--border-color-dark);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 头像上传 */
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

.dark-theme .upload-btn {
  background: var(--background-secondary);
  border-color: var(--border-color-dark);
}

.upload-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* 切换开关 */
.toggle-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}

.toggle-input {
  display: none;
}

.toggle-slider {
  position: relative;
  width: 50px;
  height: 24px;
  background: var(--border-color);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.toggle-slider::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.toggle-input:checked + .toggle-slider {
  background: var(--primary-color);
}

.toggle-input:checked + .toggle-slider::before {
  transform: translateX(26px);
}

/* 数据分析 */
.analytics-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.analytics-card {
  background: var(--background-secondary);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.dark-theme .analytics-card {
  background: var(--background-tertiary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.analytics-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
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

/* 图表占位符 */
.analytics-chart {
  background: var(--background-secondary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.dark-theme .analytics-chart {
  background: var(--background-tertiary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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

/* 动画 */
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

/* 响应式设计 */
@media (max-width: 1024px) {
  .dashboard-sidebar {
    width: 240px;
  }
  
  .dashboard-content {
    padding: 24px;
  }
  
  .posts-header,
  .post-item {
    grid-template-columns: 1fr 100px 120px 80px 100px;
  }
}

@media (max-width: 768px) {
  .dashboard {
    flex-direction: column;
  }
  
  .dashboard-sidebar {
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