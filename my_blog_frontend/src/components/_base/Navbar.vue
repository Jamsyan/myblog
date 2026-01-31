<script setup>
import { ref, inject, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { Logo, UserAvatar, Icon } from './index.js';
import SearchInput from './SearchInput.vue';
import { useNavbarContext } from './navbarContext.js';

const router = useRouter();
const route = useRoute();
const isMobileMenuOpen = ref(false);

const navbarContext = useNavbarContext();
const searchValue = ref('');

const handleSearch = () => {
  console.log('Searching for:', searchValue.value);
};

const navItems = [
  { name: '首页', path: '/' },
  { name: '探索', path: '/explore' }
];

const publicRoutes = ['/', '/explore'];

const isCollapsed = computed(() => {
  return !publicRoutes.includes(route.path);
});

const showSearch = computed(() => {
  return route.path !== '/';
});

const searchSize = computed(() => {
  if (route.path === '/explore') {
    return 'small';
  }
  return 'mini';
});

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const navigateTo = (path) => {
  router.push(path);
  isMobileMenuOpen.value = false;
};

const isActive = (path) => {
  return route.path === path;
};

const handleActionClick = (action) => {
  if (action.onClick) {
    action.onClick();
  }
};

const getIconName = (icon) => {
  const iconMap = {
    '←': 'ArrowLeft',
    '❤️': 'Heart',
    '📤': 'Share2',
    '✏️': 'Edit',
    '🎨': 'Palette'
  };
  return iconMap[icon] || null;
};
</script>

<template>
  <nav class="navbar" :class="{ collapsed: isCollapsed }">
    <div class="navbar-left-panel">
      <div class="navbar-brand">
        <Logo :size="isCollapsed ? 'small' : 'medium'" />
      </div>
      <div v-if="!isCollapsed" class="navbar-nav">
        <button v-for="item in navItems" :key="item.path" @click="navigateTo(item.path)"
          :class="['nav-item', { active: isActive(item.path) }]">
          {{ item.name }}
        </button>
      </div>
      <div v-if="isCollapsed && navbarContext.title" class="navbar-title">
        {{ navbarContext.title }}
      </div>
    </div>

    <div class="navbar-right-panel">
      <div v-if="showSearch" class="search-wrapper">
        <SearchInput v-model="searchValue" :size="searchSize" placeholder="搜索..." @search="handleSearch" />
      </div>
      <div v-if="isCollapsed && navbarContext.actions.length > 0" class="actions-wrapper">
        <button v-for="(action, index) in navbarContext.actions" :key="index" 
          @click="handleActionClick(action)"
          :class="['action-btn', action.className || '']"
          :title="action.label">
          <Icon v-if="getIconName(action.icon)" :name="getIconName(action.icon)" :size="16" class="action-icon" />
          <span v-if="action.text" class="action-text">{{ action.text }}</span>
        </button>
      </div>
      <UserAvatar :collapsed="isCollapsed" />
    </div>

    <button v-if="!isCollapsed" class="mobile-menu-btn" @click="toggleMobileMenu">
      <span class="menu-icon"></span>
      <span class="menu-icon"></span>
      <span class="menu-icon"></span>
    </button>

    <div class="mobile-menu" :class="{ open: isMobileMenuOpen }">
      <button v-for="item in navItems" :key="item.path" @click="navigateTo(item.path)"
        :class="['mobile-nav-item', { active: isActive(item.path) }]">
        {{ item.name }}
      </button>
      <button @click="navigateTo('/login')" :class="['mobile-nav-item', { active: isActive('/login') }]">
        登录
      </button>
      <button @click="navigateTo('/register')" :class="['mobile-nav-item', { active: isActive('/register') }]">
        注册
      </button>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  z-index: 1000;
  max-width: 1160px;
  margin: var(--navbar-margin-top, 20px) auto var(--navbar-margin-bottom, 20px) auto;
  left: 0;
  right: 0;
  background: rgba(245, 245, 245, 0.4);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--navbar-border-radius, 20px);
  padding: 0 var(--navbar-padding-x, 30px);
  height: var(--navbar-height, 70px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transition: 
    height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    margin 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    border-radius 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.navbar.collapsed {
  --navbar-height: 50px;
  --navbar-padding-x: 20px;
  --navbar-margin-top: 10px;
  --navbar-margin-bottom: 0;
  --navbar-border-radius: 12px;
  --navbar-gap-left: 20px;
  --navbar-gap-right: 12px;
}

.navbar-left-panel {
  display: flex;
  align-items: center;
  gap: var(--navbar-gap-left, 30px);
  width: auto;
  transition: gap 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.navbar-right-panel {
  display: flex;
  align-items: center;
  gap: var(--navbar-gap-right, 20px);
  width: auto;
  flex-shrink: 0;
  transition: gap 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-wrapper {
  width: var(--search-width, 200px);
  min-width: var(--search-min-width, 200px);
  opacity: 1;
  visibility: visible;
  transition: 
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    min-width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    opacity 0.3s ease,
    visibility 0.3s ease;
}

.navbar.collapsed .search-wrapper {
  --search-width: 180px;
  --search-min-width: 180px;
}

.actions-wrapper {
  display: flex;
  align-items: center;
  gap: var(--actions-gap, 12px);
  transition: gap 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.navbar.collapsed .actions-wrapper {
  --actions-gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--action-btn-gap, 8px);
  padding: var(--action-btn-padding-y, 8px) var(--action-btn-padding-x, 16px);
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: var(--action-btn-radius, 8px);
  cursor: pointer;
  font-size: var(--action-btn-font-size, 0.875rem);
  font-weight: 500;
  color: var(--text-primary);
  transition: 
    all 0.2s ease,
    gap 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    font-size 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    border-radius 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.navbar.collapsed .action-btn {
  --action-btn-gap: 6px;
  --action-btn-padding-y: 6px;
  --action-btn-padding-x: 12px;
  --action-btn-font-size: 0.8125rem;
  --action-btn-radius: 6px;
}

.action-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  transform: translateY(-1px);
}

.action-btn.primary {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.action-btn.primary:hover {
  background: var(--primary-hover);
}

.action-btn.danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
  border-color: rgba(239, 68, 68, 0.3);
}

.action-btn.danger:hover {
  background: var(--error-color);
  color: white;
}

.action-icon {
  font-size: 1rem;
  line-height: 1;
}

.action-text {
  font-size: 0.875rem;
  line-height: 1;
}

.navbar-title {
  font-size: var(--navbar-title-font-size, 1rem);
  font-weight: 600;
  color: var(--text-primary);
  opacity: 0;
  transform: translateX(-10px);
  transition: 
    all 0.3s ease,
    font-size 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.navbar.collapsed .navbar-title {
  opacity: 1;
  transform: translateX(0);
  --navbar-title-font-size: 0.9rem;
}

.dark-theme .navbar {
  background: rgba(30, 30, 30, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.navbar-brand {
  display: flex;
  align-items: center;
}

.navbar-nav {
  display: flex;
  gap: 24px;
  align-items: center;
  opacity: 1;
  visibility: visible;
  width: auto;
  transition: all 0.3s ease;
}

.navbar.collapsed .navbar-nav {
  opacity: 0;
  visibility: hidden;
  width: 0;
  gap: 0;
}

.nav-item {
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 500;
  padding: 12px 24px;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.nav-item:hover {
  background: var(--background-secondary);
  color: var(--primary-color);
}

.nav-item.active {
  background: var(--primary-color);
  color: white;
}

.mobile-menu-btn {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 10px;
  opacity: 1;
  visibility: visible;
  transition: all 0.3s ease;
}

.menu-icon {
  width: 24px;
  height: 2px;
  background: var(--text-primary);
  transition: all 0.3s ease;
}

.mobile-menu {
  position: fixed;
  top: 100px;
  left: 20px;
  right: 20px;
  max-width: 1160px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 20px;
  display: none;
  flex-direction: column;
  gap: 15px;
  transition: all 0.3s ease;
  z-index: 999;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.dark-theme .mobile-menu {
  background: rgba(17, 17, 17, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.mobile-nav-item {
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 500;
  padding: 12px 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.mobile-nav-item:hover {
  background: var(--background-secondary);
  color: var(--primary-color);
}

.mobile-nav-item.active {
  background: var(--primary-color);
  color: white;
}

@media (max-width: 768px) {
  .navbar-nav {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
  }

  .mobile-menu {
    display: flex;
    transform: translateY(-100%);
    opacity: 0;
    pointer-events: none;
  }

  .mobile-menu.open {
    transform: translateY(0);
    opacity: 1;
    pointer-events: auto;
  }

  .navbar-right-panel {
    gap: 10px;
  }

  .search-wrapper {
    width: 150px;
    min-width: 150px;
  }

  .actions-wrapper {
    gap: 8px;
  }

  .action-btn {
    padding: 6px 12px;
    font-size: 0.8125rem;
  }

  .action-text {
    display: none;
  }
}

@media (min-width: 769px) {
  .navbar {
    padding: 0 30px;
  }
}

@media (max-height: 700px) {
  .navbar {
    --navbar-margin-top: 15px;
    --navbar-margin-bottom: 15px;
  }

  .navbar.collapsed {
    --navbar-margin-top: 8px;
    --navbar-margin-bottom: 0;
  }
}

@media (max-height: 600px) {
  .navbar {
    --navbar-margin-top: 10px;
    --navbar-margin-bottom: 10px;
  }

  .navbar.collapsed {
    --navbar-margin-top: 5px;
    --navbar-margin-bottom: 0;
  }
}

@media (max-height: 500px) {
  .navbar {
    --navbar-margin-top: 5px;
    --navbar-margin-bottom: 5px;
  }

  .navbar.collapsed {
    --navbar-margin-top: 2px;
    --navbar-margin-bottom: 0;
  }
}
</style>