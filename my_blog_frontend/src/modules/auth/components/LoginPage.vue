<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useNavbarActions } from '../../../components/_base/navbarContext.js';
import { AcrylicGlassAnimation } from '../../../utils/authAnimations.js';
import { Icon } from '../../../components/_base/index.js';
import { login } from '../services/authService';

const router = useRouter();
const navbarActions = useNavbarActions();

const formData = reactive({
  username: '',
  password: ''
});

const errorMessage = ref('');
const isLoaded = ref(false);
const animationContainer = ref(null);
const animationCanvas = ref(null);
let lockAnimation = null;

const dailyQuotes = [
  '每一个不曾起舞的日子，都是对生命的辜负。',
  '生活不是等待风暴过去，而是学会在雨中翩翩起舞。',
  '你的时间有限，所以不要为别人而活。',
  '成功的秘诀在于坚持自己的目标和信念。',
  '今天的努力，是为了明天的自由。',
  '相信自己，你已经比想象中更强大。',
  '每一次跌倒，都是为了更好地站起来。',
  '不要因为走得太远，而忘记为什么出发。',
  '梦想不会逃跑，逃跑的永远是自己。',
  '与其抱怨黑暗，不如点亮一盏灯。',
  '人生没有白走的路，每一步都算数。',
  '做自己的太阳，无需凭借谁的光。',
  '与其仰望星空，不如成为星星。',
  '最好的时光，就是现在。',
  '愿你历尽千帆，归来仍是少年。'
];

const welcomeMessage = computed(() => {
  const randomIndex = Math.floor(Math.random() * dailyQuotes.length);
  return dailyQuotes[randomIndex];
});

const validateForm = () => {
  if (!formData.username.trim()) {
    errorMessage.value = '请输入用户名或邮箱';
    return false;
  }
  if (!formData.password) {
    errorMessage.value = '请输入密码';
    return false;
  }
  errorMessage.value = '';
  return true;
};

const handleLogin = async () => {
  if (validateForm()) {
    if (lockAnimation && lockAnimation.triggerFall) {
      lockAnimation.triggerFall();
    }

    navbarActions.setNavbarTitle('');

    try {
      const result = await login({
        username: formData.username,
        password: formData.password
      });

      navbarActions.setNavbarTitle('登录成功');

      setTimeout(() => {
        navbarActions.setNavbarTitle('');
        router.push('/profile');
      }, 1000);
    } catch (error) {
      errorMessage.value = error.message || '登录失败，请检查用户名和密码';
      if (lockAnimation && lockAnimation.reset) {
        lockAnimation.reset();
      }
    }
  }
};

const goToRegister = () => {
  router.push('/register');
};

onMounted(() => {
  navbarActions.collapseNavbar();
  navbarActions.setNavbarTitle('');

  setTimeout(() => {
    isLoaded.value = true;
  }, 100);

  setTimeout(() => {
    initLockAnimation();
  }, 200);
});

onUnmounted(() => {
  navbarActions.setNavbarTitle('');
  if (lockAnimation) {
    lockAnimation.destroy();
    lockAnimation = null;
  }
});

const initLockAnimation = () => {
  if (!animationCanvas.value) return;

  const container = animationContainer.value;
  const canvas = animationCanvas.value;
  const rect = container.getBoundingClientRect();

  canvas.width = rect.width;
  canvas.height = rect.height;

  const themeName = document.body.className.includes('theme-danqing-blue') ? 'theme-danqing-blue' :
    document.body.className.includes('theme-fenxia-purple') ? 'theme-fenxia-purple' :
      'theme-china-red';

  lockAnimation = new AcrylicGlassAnimation(canvas, {
    size: Math.min(rect.width, rect.height) * 0.9,
    themeName: themeName
  });

  lockAnimation.start();

  const resizeObserver = new ResizeObserver(() => {
    if (lockAnimation && container) {
      const newRect = container.getBoundingClientRect();
      lockAnimation.resize(newRect.width, newRect.height);
    }
  });

  resizeObserver.observe(container);
};
</script>

<template>
  <div class="login-container" :class="{ loaded: isLoaded }">
    <div class="login-content">
      <div class="left-panel">
        <h2 class="login-title">
          <svg class="quote-svg" viewBox="0 0 400 60">
            <defs>
              <linearGradient id="quoteGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:var(--primary-color);stop-opacity:1" />
                <stop offset="100%" style="stop-color:var(--secondary-color);stop-opacity:1" />
              </linearGradient>
            </defs>
            <text x="200" y="35" font-size="26" font-weight="700" fill="url(#quoteGradient)" text-anchor="middle">
              {{ welcomeMessage }}
            </text>
          </svg>
        </h2>
        <p class="login-description">登录您的账户继续</p>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleLogin" class="form">
          <div class="form-group">
            <label for="username">用户名/邮箱</label>
            <input type="text" id="username" v-model="formData.username" placeholder="请输入用户名或邮箱" class="form-input" />
          </div>

          <div class="form-group">
            <label for="password">密码</label>
            <input type="password" id="password" v-model="formData.password" placeholder="请输入密码" class="form-input" />
          </div>

          <button type="submit" class="login-button">
            登录
          </button>

          <button type="button" @click="goToRegister" class="register-button">
            还没有账号？立即注册
          </button>
        </form>
      </div>

      <div class="right-panel">
        <div class="animation-wrapper" ref="animationContainer">
          <canvas ref="animationCanvas" class="animation-canvas"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  position: relative;
  z-index: 1;
  background: transparent;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-container.loaded {
  opacity: 1;
  transform: translateY(0);
}

.login-content {
  display: flex;
  width: 100%;
  max-width: 900px;
  min-height: 450px;
  margin: 20px auto;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(30px) saturate(180%);
  -webkit-backdrop-filter: blur(30px) saturate(180%);
  border-radius: 24px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.12),
    0 2px 8px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  overflow: hidden;
  transform: scale(0.95);
  opacity: 0;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) 0.1s;
}

.login-container.loaded .login-content {
  transform: scale(1);
  opacity: 1;
}

.left-panel {
  flex: 0 0 60%;
  padding: 35px 50px;
  display: flex;
  flex-direction: column;
}

.right-panel {
  flex: 0 0 40%;
  background: linear-gradient(135deg, rgba(198, 40, 40, 0.15), rgba(229, 57, 53, 0.15));
  backdrop-filter: blur(20px) saturate(150%);
  -webkit-backdrop-filter: blur(20px) saturate(150%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border-left: 1px solid rgba(255, 255, 255, 0.2);
}

.animation-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-title {
  color: var(--text-primary);
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 8px;
  line-height: 1.5;
  min-height: 60px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
}

.quote-svg {
  width: 100%;
  height: 60px;
  overflow: hidden;
  max-width: 100%;
  display: block;
}

.quote-svg text {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  animation: quoteDraw 1.5s ease-out 0.3s both;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@keyframes quoteDraw {
  0% {
    opacity: 0;
    transform: translateY(10px);
    filter: blur(4px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

.login-description {
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 25px;
}

.error-message {
  background-color: rgba(244, 67, 54, 0.1);
  color: var(--error-color);
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 20px;
  text-align: center;
  font-size: 14px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
}

.form-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 14px 16px;
  color: var(--text-primary);
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-input::placeholder {
  color: var(--text-secondary);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(198, 40, 40, 0.1);
  transform: translateY(-1px);
}

.login-button {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: none;
  border-radius: 12px;
  padding: 14px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 5px;
}

.login-button:hover {
  background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(198, 40, 40, 0.3);
}

.login-button:active {
  transform: translateY(0);
}

.register-button {
  background: rgba(0, 0, 0, 0.05);
  border: none;
  border-radius: 12px;
  padding: 14px;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 5px;
}

.register-button:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.animation-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

@media (max-width: 968px) {
  .login-content {
    margin: 10px;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px) saturate(150%);
    -webkit-backdrop-filter: blur(20px) saturate(150%);
  }

  .left-panel {
    padding: 20px;
  }

  .right-panel {
    display: none;
  }

  .login-title {
    font-size: 20px;
  }

  .quote-svg text {
    font-size: 20px;
  }
}
</style>