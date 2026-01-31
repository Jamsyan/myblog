<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useFooterState } from '../../utils/footerState';
import { Logo } from './index.js';

const props = defineProps({
  copyright: {
    type: String,
    default: '© 2024 锦年志. All rights reserved.'
  },
  icpInfo: {
    type: String,
    default: '京ICP备2024000000号'
  },
  contactInfo: {
    type: Object,
    default: () => ({
      email: 'contact@jinianzhi.com',
      github: 'https://github.com/jinianzhi',
      wechat: 'jinianzhi_official'
    })
  },
  links: {
    type: Array,
    default: () => [
      { name: '关于我们', href: '#about' },
      { name: '隐私政策', href: '#privacy' },
      { name: '使用条款', href: '#terms' }
    ]
  },
  detectionArea: {
    type: Number,
    default: 50
  },
  hideDelay: {
    type: Number,
    default: 2000
  },
  enableOnPages: {
    type: Array,
    default: () => ['/']
  },
  autoHideOnRouteChange: {
    type: Boolean,
    default: true
  }
});

const route = useRoute();
const { setFooterVisible, setFooterHeight } = useFooterState();

const isVisible = ref(false);
const isHovering = ref(false);
const hideTimer = ref(null);
const footerRef = ref(null);

const isPageAllowed = () => {
  const allowed = props.enableOnPages.includes(route.path);
  return allowed;
};

const checkMousePosition = (event) => {
  if (!isPageAllowed()) {
    return;
  }

  const { clientX, clientY } = event;
  const { innerWidth, innerHeight } = window;
  const { detectionArea } = props;

  const isAtLeftEdge = clientX <= detectionArea;
  const isAtRightEdge = clientX >= innerWidth - detectionArea;
  const isAtBottomEdge = clientY >= innerHeight - detectionArea;

  if (isAtLeftEdge || isAtRightEdge || isAtBottomEdge) {
    showFooter();
  } else if (!isHovering.value) {
    startHideTimer();
  }
};

const showFooter = () => {
  if (!isPageAllowed()) {
    return;
  }

  if (hideTimer.value) {
    clearTimeout(hideTimer.value);
    hideTimer.value = null;
  }
  isVisible.value = true;
  setFooterVisible(true);
  
  nextTick(() => {
    if (footerRef.value) {
      const height = footerRef.value.offsetHeight;
      setFooterHeight(height);
    }
  });
};

const startHideTimer = () => {
  if (hideTimer.value) {
    clearTimeout(hideTimer.value);
  }
  hideTimer.value = setTimeout(() => {
    if (!isHovering.value) {
      isVisible.value = false;
      setFooterVisible(false);
    }
  }, props.hideDelay);
};

const handleMouseEnter = () => {
  if (!isPageAllowed()) return;
  isHovering.value = true;
  showFooter();
};

const handleMouseLeave = () => {
  isHovering.value = false;
  startHideTimer();
};

const resetFooterState = () => {
  if (hideTimer.value) {
    clearTimeout(hideTimer.value);
    hideTimer.value = null;
  }
  isVisible.value = false;
  isHovering.value = false;
};

watch(
  () => route.path,
  () => {
    if (props.autoHideOnRouteChange) {
      resetFooterState();
    }
  }
);

onMounted(() => {
  window.addEventListener('mousemove', checkMousePosition);
});

onUnmounted(() => {
  window.removeEventListener('mousemove', checkMousePosition);
  if (hideTimer.value) {
    clearTimeout(hideTimer.value);
  }
});
</script>

<template>
  <footer 
    ref="footerRef"
    class="footer" 
    :class="{ visible: isVisible }"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <div class="footer-content">
      <div class="footer-info">
        <div class="footer-brand">
          <Logo size="small" :with-link="false" />
        </div>
      </div>
      <div class="footer-links">
        <div class="links-list">
          <a
            v-for="link in links"
            :key="link.name"
            :href="link.href"
            class="link-item"
            @click.prevent
          >
            {{ link.name }}
          </a>
        </div>
      </div>
      <div class="footer-contact">
        <div class="contact-list">
          <a 
            v-if="contactInfo.email" 
            :href="`mailto:${contactInfo.email}`" 
            class="contact-item"
          >
            {{ contactInfo.email }}
          </a>
          <a 
            v-if="contactInfo.github" 
            :href="contactInfo.github" 
            target="_blank" 
            class="contact-item"
          >
            GitHub
          </a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="footer-copyright">
        {{ copyright }}
      </div>
      <div class="footer-icp">
        {{ icpInfo }}
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  position: fixed;
  bottom: 30px;
  left: 30px;
  right: 30px;
  z-index: 999;
  max-width: 1140px;
  margin: 0 auto;
  background: rgba(245, 245, 245, 0.4);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  padding: 15px 20px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.3);
  opacity: 0;
  transform: translateY(50px) scale(0.95);
  pointer-events: none;
  box-sizing: border-box;
}

.footer.visible {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.dark-theme .footer {
  background: rgba(30, 30, 30, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.footer-content {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  margin-bottom: 15px;
  align-items: start;
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-brand {
  display: flex;
  align-items: center;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.link-item {
  color: var(--text-secondary);
  font-size: 0.8rem;
  text-decoration: none;
  transition: all 0.3s ease;
  padding: 3px 0;
}

.link-item:hover {
  color: var(--primary-color);
  padding-left: 6px;
}

.footer-contact {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.contact-item {
  color: var(--text-secondary);
  font-size: 0.8rem;
  text-decoration: none;
  transition: all 0.3s ease;
  padding: 3px 0;
}

.contact-item:hover {
  color: var(--primary-color);
  padding-left: 6px;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.dark-theme .footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-copyright,
.footer-icp {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

@media (max-width: 768px) {
  .footer {
    bottom: 20px;
    left: 20px;
    right: 20px;
    padding: 12px 15px;
    border-radius: 15px;
  }
  .footer-content {
    grid-template-columns: 1fr;
    gap: 15px;
    text-align: center;
  }
  .footer-info,
  .footer-links,
  .footer-contact {
    align-items: center;
  }
  .links-list,
  .contact-list {
    align-items: center;
  }
  .link-item,
  .contact-item {
    padding: 4px 0;
  }
  .link-item:hover,
  .contact-item:hover {
    padding-left: 0;
    padding-right: 0;
  }
  .footer-bottom {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 5px;
  }
}

@media (max-width: 480px) {
  .footer {
    padding: 10px 12px;
  }
  .link-item,
  .contact-item {
    font-size: 0.75rem;
    padding: 3px 6px;
  }
  .footer-copyright,
  .footer-icp {
    font-size: 0.65rem;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes slideDown {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
}

.footer.visible {
  animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.footer:not(.visible) {
  animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>