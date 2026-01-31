<script setup>
import { ref, computed, onMounted, inject } from 'vue';
import { useRouter } from 'vue-router';
import { isAuthenticated, getCurrentUser } from '../../modules/auth/services/authService';
import { Icon } from './index.js';

const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  collapsed: {
    type: Boolean,
    default: false
  },
  customAvatar: {
    type: String,
    default: null
  }
});

const router = useRouter();
const user = ref(null);
const isLoading = ref(false);
const triggerSplit = inject('triggerSplit', null);

const sizeMap = {
  small: 28,
  medium: 36,
  large: 44
};

const avatarSize = computed(() => {
  if (props.collapsed) {
    return sizeMap.small;
  }
  return sizeMap[props.size];
});

const avatarSizeStyle = computed(() => {
  return {
    width: `${avatarSize.value}px`,
    height: `${avatarSize.value}px`
  };
});

const generateRandomAvatar = (username) => {
  if (!username) return null;
  const encodedName = encodeURIComponent(username);
  return `https://ui-avatars.com/api/?name=${encodedName}&background=e0e0e0&color=fff&size=${avatarSize.value}`;
};

const avatarUrl = computed(() => {
  if (props.customAvatar) {
    return props.customAvatar;
  }
  
  if (user.value && user.value.avatar) {
    return user.value.avatar;
  }
  
  if (user.value && user.value.username) {
    return generateRandomAvatar(user.value.username);
  }
  
  return null;
});

const handleAvatarClick = () => {
  if (isLoading.value) return;
  
  if (isAuthenticated()) {
    router.push('/profile');
  } else {
    isLoading.value = true;
    if (triggerSplit) {
      triggerSplit();
    }
    setTimeout(() => {
      isLoading.value = false;
      router.push('/login');
    }, 300);
  }
};

const checkAuthStatus = () => {
  user.value = getCurrentUser();
};

onMounted(() => {
  checkAuthStatus();
});
</script>

<template>
  <button 
    class="user-avatar-btn" 
    @click="handleAvatarClick" 
    :class="{ loading: isLoading, collapsed }"
    :style="avatarSizeStyle"
  >
    <div v-if="isLoading" class="loading-spinner"></div>
    
    <Icon v-else-if="!avatarUrl" name="User" :size="avatarSize * 0.6" class="default-avatar-icon" />
    
    <img v-else :src="avatarUrl" :alt="user?.username || 'User avatar'" class="user-avatar-img" />
  </button>
</template>

<style scoped>
.user-avatar-btn {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(0, 0, 0, 0.1);
  cursor: pointer;
  padding: 0;
  border-radius: 50%;
  transition: 
    all 0.2s ease,
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
}

.user-avatar-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: var(--primary-color);
  transform: scale(1.1);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 0, 0, 0.05);
}

.dark-theme .user-avatar-btn {
  background: rgba(40, 40, 40, 0.8);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark-theme .user-avatar-btn:hover {
  background: rgba(50, 50, 50, 0.95);
  border-color: var(--primary-color);
}

.user-avatar-btn.collapsed {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.05);
}

.user-avatar-btn.collapsed:hover {
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
}

.user-avatar-btn.loading {
  pointer-events: none;
  opacity: 0.7;
}

.default-avatar-icon {
  color: var(--text-secondary);
  transition: all 0.2s ease;
  width: 60%;
  height: 60%;
}

.user-avatar-btn:hover .default-avatar-icon {
  color: var(--primary-color);
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.loading-spinner {
  width: 60%;
  height: 60%;
  border: 2px solid var(--primary-color);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
