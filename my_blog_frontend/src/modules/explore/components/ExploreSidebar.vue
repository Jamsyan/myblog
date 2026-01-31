<script setup>
import { ref, onMounted } from 'vue';
import { useExploreStore } from '../store';
import { getPostTypes } from '../services/postService';

// 使用状态管理
const { state, setPostTypes } = useExploreStore();

// 当前选中的类型
const selectedType = ref('all');

// 移动端侧边栏展开状态
const isSidebarOpen = ref(true);

// 加载帖子类型
const loadPostTypes = async () => {
  try {
    const types = await getPostTypes();
    setPostTypes(types);
  } catch (error) {
    console.error('Failed to load post types:', error);
  }
};

// 组件挂载时加载类型
onMounted(() => {
  loadPostTypes();
});

// 切换类型
const handleTypeSelect = (typeId) => {
  selectedType.value = typeId;
  // 触发类型变更事件
  emit('typeChange', typeId);
};

// 切换侧边栏展开状态
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

// 定义事件
const emit = defineEmits(['typeChange']);
</script>

<template>
  <div class="explore-sidebar">
    <!-- 侧边栏头部 -->
    <div class="sidebar-header">
      <h2>帖子类型</h2>
      <button class="toggle-btn" @click="toggleSidebar">
        {{ isSidebarOpen ? '收起' : '展开' }}
      </button>
    </div>
    
    <!-- 类型列表 -->
    <div class="type-list" v-show="isSidebarOpen">
      <button
        v-for="type in state.postTypes"
        :key="type.id"
        class="type-item"
        :class="{ active: selectedType === type.id }"
        @click="handleTypeSelect(type.id)"
      >
        {{ type.name }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.explore-sidebar {
  width: 100%;
  background-color: var(--card-background);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
  height: fit-content;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 深色主题适配 */
.dark-theme .explore-sidebar {
  background-color: rgba(30, 30, 30, 0.7);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.sidebar-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.toggle-btn {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background-color: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background-color: var(--hover-background);
  border-color: var(--primary-color);
}

.type-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.type-item {
  padding: 0.75rem 1rem;
  text-align: left;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background-color: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9375rem;
}

.type-item:hover {
  background-color: var(--hover-background);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.type-item.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .explore-sidebar {
    width: 100%;
    margin-bottom: 1.5rem;
  }
  
  .sidebar-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .toggle-btn {
    align-self: stretch;
  }
}
</style>