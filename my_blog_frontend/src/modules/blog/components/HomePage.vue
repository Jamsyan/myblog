<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { SearchInput, Logo } from '../../../components/_base';
import { useFooterState } from '../../../utils/footerState';

const searchQuery = ref('');
const { subscribe } = useFooterState();
const contentRef = ref(null);
const isFooterVisible = ref(false);

const handleSearch = () => {
};

// 简化布局：使用固定位置
const contentStyle = computed(() => {
  // 根据页脚显示状态设置不同的固定位置
  const topPosition = isFooterVisible.value ? '80px' : '150px';

  return {
    position: 'absolute',
    top: topPosition,
    left: '50%',
    transform: 'translateX(-50%)',
    transition: 'top 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
  };
});

const handleFooterStateChange = (state) => {
  isFooterVisible.value = state.visible;
};

onMounted(() => {
  const unsubscribe = subscribe(handleFooterStateChange);

  onUnmounted(() => {
    unsubscribe();
  });
});
</script>

<template>
  <div class="home-page">
    <div ref="contentRef" class="home-page__content" :style="contentStyle">
      <div class="home-page__logo">
        <Logo size="xlarge" :with-link="false" />
      </div>
      <p class="home-page__subtitle">这里是锦年志，你的日志日记</p>
      <div class="home-page__search">
        <SearchInput v-model="searchQuery" size="large" placeholder="输入关键词搜索..." @search="handleSearch" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  position: relative;
  width: 100%;
  height: calc(100vh - 120px);
  overflow: hidden;
}

.home-page__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 800px;
  width: 100%;
  text-align: center;
  z-index: 1;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 20px;
  box-shadow: var(--shadow-lg);
}

.home-page__logo {
  margin-bottom: 1rem;
}

.home-page__subtitle {
  font-size: 1.2rem;
  margin-bottom: 3rem;
  color: var(--text-secondary);
  max-width: 600px;
}

.home-page__search {
  width: 100%;
  max-width: 600px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-page {
    height: calc(100vh - 110px);
  }

  .home-page__subtitle {
    font-size: 1rem;
    margin-bottom: 2rem;
  }

  .home-page__search {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .home-page__subtitle {
    font-size: 0.9rem;
  }
}
</style>