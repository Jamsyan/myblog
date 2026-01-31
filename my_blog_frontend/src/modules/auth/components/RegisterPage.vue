<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useNavbarActions } from '../../../components/_base/navbarContext.js';
import { FlowLightAnimation, GeometryMatrixAnimation, AtlantisRedFlashAnimation, PreciseCheckmarkAnimation } from '../../../utils/authAnimations.js';
import { Icon } from '../../../components/_base/index.js';
import { register, login } from '../services/authService';

const router = useRouter();
const navbarActions = useNavbarActions();

const currentStep = ref(1);
const totalSteps = 4;
const animationContainer = ref(null);
const animationCanvas = ref(null);
let currentAnimation = null;

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  nickname: '',
  bio: ''
});

const validateStep1 = () => {
  if (!formData.username.trim()) {
    navbarActions.setNavbarTitle('请输入用户名');
    return false;
  }
  if (!formData.email.trim()) {
    navbarActions.setNavbarTitle('请输入邮箱');
    return false;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    navbarActions.setNavbarTitle('请输入有效的邮箱地址');
    return false;
  }
  navbarActions.setNavbarTitle('');
  return true;
};

const validateStep2 = () => {
  if (!formData.password) {
    navbarActions.setNavbarTitle('请输入密码');
    return false;
  }
  if (formData.password.length < 6) {
    navbarActions.setNavbarTitle('密码长度至少为6位');
    return false;
  }
  if (formData.password !== formData.confirmPassword) {
    navbarActions.setNavbarTitle('两次输入的密码不一致');
    return false;
  }
  navbarActions.setNavbarTitle('');
  return true;
};

const nextStep = () => {
  if (currentStep.value === 1 && validateStep1()) {
    currentStep.value++;
  } else if (currentStep.value === 2 && validateStep2()) {
    currentStep.value++;
  } else if (currentStep.value === 3) {
    navbarActions.setNavbarTitle('');
    currentStep.value++;
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    navbarActions.setNavbarTitle('');
    currentStep.value--;
  }
};

const skipStep = () => {
  if (currentStep.value === 3) {
    currentStep.value++;
  }
};

const handleRegister = async () => {
  try {
    await register({
      username: formData.username,
      email: formData.email,
      password: formData.password,
      full_name: formData.nickname || formData.username
    });

    navbarActions.setNavbarTitle('注册成功');

    setTimeout(async () => {
      try {
        await login({
          username: formData.username,
          password: formData.password
        });

        router.push('/profile');
      } catch (error) {
        console.error('自动登录失败:', error);
        router.push('/login');
      }
    }, 2000);
  } catch (error) {
    navbarActions.setNavbarTitle(error.message || '注册失败');
    currentStep.value = 1;
  }
};

const goToLogin = () => {
  router.push('/login');
};

watch(currentStep, (newStep) => {
  updateAnimation(newStep);
});

const progressPercentage = computed(() => {
  return ((currentStep.value - 1) / (totalSteps - 1)) * 100;
});

const updateAnimation = (step) => {
  if (!animationCanvas.value) return;

  if (currentAnimation) {
    currentAnimation.destroy();
    currentAnimation = null;
  }

  const container = animationContainer.value;
  const canvas = animationCanvas.value;
  const rect = container.getBoundingClientRect();

  canvas.width = rect.width;
  canvas.height = rect.height;

  const themeName = document.body.className.includes('theme-danqing-blue') ? 'theme-danqing-blue' :
    document.body.className.includes('theme-fenxia-purple') ? 'theme-fenxia-purple' :
      'theme-china-red';

  const size = Math.min(rect.width, rect.height) * 0.9;

  switch (step) {
    case 1:
      currentAnimation = new FlowLightAnimation(canvas, { size, themeName });
      break;
    case 2:
      currentAnimation = new GeometryMatrixAnimation(canvas, { size, themeName });
      break;
    case 3:
      currentAnimation = new AtlantisRedFlashAnimation(canvas, { size, themeName });
      break;
    case 4:
      currentAnimation = new PreciseCheckmarkAnimation(canvas, { size: size * 0.85, themeName });
      break;
  }

  if (currentAnimation) {
    currentAnimation.start();

    if (step < 4) {
      setTimeout(() => {
        currentAnimation.play();
      }, 100);
    } else {
      setTimeout(() => {
        currentAnimation.play();
      }, 200);
    }
  }

  const resizeObserver = new ResizeObserver(() => {
    if (currentAnimation && container) {
      const newRect = container.getBoundingClientRect();
      currentAnimation.resize(newRect.width, newRect.height);
    }
  });

  resizeObserver.observe(container);
};

onMounted(() => {
  navbarActions.collapseNavbar();
  navbarActions.setNavbarTitle('');

  setTimeout(() => {
    updateAnimation(currentStep.value);
  }, 300);
});

onUnmounted(() => {
  navbarActions.setNavbarTitle('');
  if (currentAnimation) {
    currentAnimation.destroy();
    currentAnimation = null;
  }
});
</script>

<template>
  <div class="register-container">
    <div class="register-content">
      <div class="left-panel">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>

        <div class="steps-indicator">
          <div v-for="step in totalSteps" :key="step"
            :class="['step-dot', { active: currentStep === step, completed: currentStep > step }]">
            <span class="step-number">{{ step }}</span>
          </div>
        </div>

        <div class="form-container">
          <transition name="slide-fade" mode="out-in">
            <div v-if="currentStep === 1" key="step1" class="step-content">
              <h2 class="step-title">创建您的账户</h2>
              <p class="step-description">让我们从基本信息开始</p>

              <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" id="username" v-model="formData.username" placeholder="请输入用户名" class="form-input" />
              </div>

              <div class="form-group">
                <label for="email">邮箱</label>
                <input type="email" id="email" v-model="formData.email" placeholder="请输入邮箱" class="form-input" />
              </div>
            </div>

            <div v-else-if="currentStep === 2" key="step2" class="step-content">
              <h2 class="step-title">设置密码</h2>
              <p class="step-description">保护您的账户安全</p>

              <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" v-model="formData.password" placeholder="请输入密码（至少6位）"
                  class="form-input" />
              </div>

              <div class="form-group">
                <label for="confirmPassword">确认密码</label>
                <input type="password" id="confirmPassword" v-model="formData.confirmPassword" placeholder="请再次输入密码"
                  class="form-input" />
              </div>
            </div>

            <div v-else-if="currentStep === 3" key="step3" class="step-content">
              <h2 class="step-title">完善个人资料</h2>
              <p class="step-description">让其他人更好地了解您（可选）</p>

              <div class="form-group">
                <label for="nickname">昵称</label>
                <input type="text" id="nickname" v-model="formData.nickname" placeholder="请输入昵称" class="form-input" />
              </div>

              <div class="form-group">
                <label for="bio">个人简介</label>
                <textarea id="bio" v-model="formData.bio" placeholder="介绍一下自己..." class="form-textarea"
                  rows="3"></textarea>
              </div>
            </div>

            <div v-else-if="currentStep === 4" key="step4" class="step-content success">
              <div class="success-icon">
                <Icon name="CheckCircle" :size="80" />
              </div>
              <h2 class="step-title">注册成功！</h2>
              <p class="step-description">欢迎加入我们的社区</p>
              <button @click="handleRegister" class="continue-button">
                前往登录
              </button>
            </div>
          </transition>

          <div v-if="currentStep < 4" class="button-group">
            <button v-if="currentStep > 1" @click="prevStep" class="prev-button">
              上一步
            </button>
            <button @click="nextStep" class="next-button">
              {{ currentStep === 3 ? '完成注册' : '下一步' }}
            </button>
            <button v-if="currentStep === 3" @click="skipStep" class="skip-button">
              跳过
            </button>
          </div>

          <button v-if="currentStep < 4" @click="goToLogin" class="login-link-button">
            已有账号？立即登录
          </button>
        </div>
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
.register-container {
  min-height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  position: relative;
  z-index: 1;
  background: transparent;
}

.register-content {
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
}

.animation-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1000px;
  overflow: hidden;
}

.animation-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
  margin-bottom: 20px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.steps-indicator {
  display: flex;
  gap: 12px;
  margin-bottom: 25px;
}

.step-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.step-dot.active {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  box-shadow: 0 2px 8px rgba(var(--primary-rgb), 0.3);
}

.step-dot.completed {
  background: var(--light-color);
}

.step-number {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.form-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.step-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.step-title {
  color: var(--text-primary);
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 6px;
  line-height: 1.5;
}

.step-description {
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
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
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.1);
  transform: translateY(-1px);
}

.form-textarea {
  width: 100%;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 14px 16px;
  color: var(--text-primary);
  font-size: 16px;
  transition: all 0.3s ease;
  resize: none;
  font-family: inherit;
}

.form-textarea::placeholder {
  color: var(--text-secondary);
}

.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.1);
  transform: translateY(-1px);
}

.button-group {
  display: flex;
  gap: 16px;
  margin-top: auto;
}

.prev-button {
  flex: 1;
  background: rgba(0, 0, 0, 0.05);
  border: none;
  border-radius: 12px;
  padding: 14px;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.prev-button:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.next-button {
  flex: 2;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: none;
  border-radius: 12px;
  padding: 14px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.next-button:hover {
  background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
}

.next-button:active {
  transform: translateY(0);
}

.skip-button {
  flex: 1;
  background: rgba(0, 0, 0, 0.05);
  border: none;
  border-radius: 12px;
  padding: 14px;
  color: var(--text-secondary);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.skip-button:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.continue-button {
  width: 100%;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: none;
  border-radius: 12px;
  padding: 14px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 20px;
}

.continue-button:hover {
  background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
}

.login-link-button {
  background: rgba(0, 0, 0, 0.05);
  border: none;
  border-radius: 12px;
  padding: 14px;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 16px;
  width: 100%;
}

.login-link-button:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.success {
  align-items: center;
  justify-content: center;
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.success-icon svg {
  width: 100%;
  height: 100%;
}

.success-icon circle {
  stroke: var(--success-color);
  stroke-width: 2;
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}

.success-icon path {
  stroke: var(--success-color);
  stroke-width: 2;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}

@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}

.animation-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1000px;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

@media (max-width: 968px) {
  .register-content {
    flex-direction: column;
    margin: 20px;
    min-height: auto;
  }

  .left-panel {
    flex: 1;
    padding: 30px;
  }

  .right-panel {
    flex: 0 0 200px;
    background: linear-gradient(135deg, rgba(198, 40, 40, 0.12), rgba(229, 57, 53, 0.12));
  }

  .step-title {
    font-size: 24px;
  }

  .animation-wrapper {
    perspective: 600px;
  }
}

@media (max-width: 640px) {
  .register-content {
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

  .step-title {
    font-size: 20px;
  }

  .button-group {
    flex-direction: column;
  }
}
</style>