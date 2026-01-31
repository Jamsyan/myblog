<script setup>
import { useProfileStore } from '../store';
import { Icon } from '../../../components/_base/index.js';

const { state, themes, setTheme } = useProfileStore();

const handleThemeChange = (themeId) => {
  setTheme(themeId);
};
</script>

<template>
  <div class="theme-settings">
    <h2>主题设置</h2>
    <p class="description">选择你喜欢的主题颜色</p>
    
    <div class="theme-grid">
      <div
        v-for="theme in themes"
        :key="theme.id"
        class="theme-card"
        :class="{ active: state.theme === theme.id }"
        @click="handleThemeChange(theme.id)"
      >
        <div class="theme-preview" :class="`theme-${theme.id}`"></div>
        <div class="theme-info">
          <h3>{{ theme.name }}</h3>
          <div class="theme-indicator" v-if="state.theme === theme.id">
            <Icon name="Check" :size="16" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.theme-settings {
  padding: 24px;
}

.theme-settings h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.description {
  color: var(--text-secondary);
  margin-bottom: 32px;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.theme-card {
  background: var(--card-background);
  backdrop-filter: blur(10px);
  border: 2px solid transparent;
  border-radius: var(--border-radius-lg);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-md);
}

.theme-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.theme-card.active {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(198, 40, 40, 0.1);
}

.theme-preview {
  width: 100%;
  height: 80px;
  border-radius: var(--border-radius-md);
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.theme-preview.theme-china-red {
  background: linear-gradient(135deg, #C62828 0%, #E53935 100%);
}

.theme-preview.theme-danqing-blue {
  background: linear-gradient(135deg, #0D47A1 0%, #1976D2 100%);
}

.theme-preview.theme-fenxia-purple {
  background: linear-gradient(135deg, #7B1FA2 0%, #9C27B0 100%);
}

.theme-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.theme-info h3 {
  font-size: 1rem;
  font-weight: 500;
  margin: 0;
  color: var(--text-primary);
}

.theme-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
}

@media (max-width: 768px) {
  .theme-grid {
    grid-template-columns: 1fr;
  }
}
</style>