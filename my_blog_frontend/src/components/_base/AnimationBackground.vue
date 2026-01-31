<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { ColorEngine } from '../../utils/colorEngine.js';
import { ParticleFlow, WaveRipple, AuroraEffect } from '../../utils/animationAlgorithms.js';
import {
  FlameParticleFlow,
  RisingWaveFlow,
  PulseGlow,
  SilkFlow,
  BreathingPulse,
  MistEffect,
  InkDiffusion,
  BambooLeaves,
  CloudMist
} from '../../utils/themeAnimations.js';
import {
  PerformanceMonitor,
  DynamicParameterAdjuster,
  CanvasRendererOptimizer
} from '../../utils/animationPerformance.js';
import { generateAnimationConfig } from '../../config/animationConfig.js';

// 组件属性
const props = defineProps({
  preset: {
    type: String,
    default: 'flow'
  },
  intensity: {
    type: String,
    default: 'medium'
  }
});

// 响应式数据
const canvasRef = ref(null);
const animationId = ref(null);
const currentTheme = ref('theme-china-red');
const effects = ref({});
const config = ref(null);

// 性能优化相关
const performanceMonitor = new PerformanceMonitor();
const parameterAdjuster = new DynamicParameterAdjuster();
let rendererOptimizer = null;

// 初始化动画效果
function initEffects() {
  try {
    config.value = generateAnimationConfig(currentTheme.value, props.preset);
    
    // 验证配置
    if (!config.value) {
      console.error('Config is null!');
      return;
    }
    
    if (!config.value.colors || config.value.colors.length === 0) {
      console.error('No colors available!');
      return;
    }
    
    if (!config.value.themeConfig || !config.value.themeConfig.effects) {
      console.error('Invalid themeConfig!');
      return;
    }
    
    // 根据性能级别调整参数
    parameterAdjuster.adjustByPerformanceLevel(config.value.performance);
    
    // 默认配置
    const defaultConfigs = {
      flameParticleFlow: {
        maxParticles: 200,
        maxLanterns: 6,
        maxFireworks: 3,
        maxClouds: 3,
        speed: 1.5
      },
      risingWaveFlow: {
        maxWaves: 4,
        speed: 0.8
      },
      pulseGlow: {
        maxPulses: 3,
        speed: 0.5
      },
      silkFlow: {
        maxCurves: 10,
        maxMists: 15,
        speed: 0.5
      },
      breathingPulse: {
        maxOrbs: 10,
        speed: 0.02
      },
      mistEffect: {
        maxMists: 8,
        speed: 0.3
      },
      inkDiffusion: {
        maxInkSpots: 15,
        maxBambooLeaves: 20,
        maxClouds: 8,
        speed: 0.5
      },
      bambooLeaves: {
        maxLeaves: 20,
        speed: 0.8
      },
      cloudMist: {
        maxClouds: 6,
        speed: 0.4
      },
      particleFlow: {
        maxParticles: 100,
        speed: 1.0
      },
      waveRipple: {
        maxRipples: 5,
        speed: 0.8
      },
      auroraEffect: {
        maxWaves: 3,
        speed: 0.5
      }
    };
    
    // 创建动画效果实例
    const effectClasses = {
      // 通用效果
      particleFlow: ParticleFlow,
      waveRipple: WaveRipple,
      auroraEffect: AuroraEffect,
      
      // 中国红主题专用效果
      flameParticleFlow: FlameParticleFlow,
      risingWaveFlow: RisingWaveFlow,
      pulseGlow: PulseGlow,
      
      // 粉霞紫主题专用效果
      silkFlow: SilkFlow,
      breathingPulse: BreathingPulse,
      mistEffect: MistEffect,
      
      // 丹青蓝主题专用效果
      inkDiffusion: InkDiffusion,
      bambooLeaves: BambooLeaves,
      cloudMist: CloudMist
    };

    effects.value = {};
    
    config.value.effects.forEach(effectName => {
      try {
        const EffectClass = effectClasses[effectName];
        if (EffectClass) {
          const effectConfig = config.value.themeConfig.effects[effectName] || {};
          
          // 合并默认配置
          const mergedConfig = { ...defaultConfigs[effectName], ...effectConfig };
          
          // 应用性能调整
          const adjustedConfig = {};
          Object.keys(mergedConfig).forEach(key => {
            if (typeof mergedConfig[key] === 'number') {
              if (key.includes('max') || key.includes('Count')) {
                adjustedConfig[key] = parameterAdjuster.adjustParticleCount(mergedConfig[key]);
              } else if (key.includes('speed')) {
                adjustedConfig[key] = parameterAdjuster.adjustAnimationSpeed(mergedConfig[key]);
              } else {
                adjustedConfig[key] = mergedConfig[key];
              }
            } else {
              adjustedConfig[key] = mergedConfig[key];
            }
          });
          
          effects.value[effectName] = new EffectClass({
            ...adjustedConfig,
            colors: config.value.colors
          });
        } else {
          console.warn(`Effect class not found: ${effectName}`);
        }
      } catch (error) {
        console.error(`Failed to create effect ${effectName}:`, error);
      }
    });

    // 初始化渲染优化器
    if (canvasRef.value && !rendererOptimizer) {
      rendererOptimizer = new CanvasRendererOptimizer(canvasRef.value);
      rendererOptimizer.optimizeRenderSettings(config.value.performance);
    }
  } catch (error) {
    console.error('Error initializing effects:', error);
  }
}

// 检测当前主题
function detectTheme() {
  const body = document.body;
  const themes = ['theme-china-red', 'theme-danqing-blue', 'theme-fenxia-purple'];

  for (const theme of themes) {
    if (body.classList.contains(theme)) {
      return theme;
    }
  }

  return 'theme-china-red'; // 默认主题
}

// 监听主题变化
function watchTheme() {
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.attributeName === 'class') {
        const newTheme = detectTheme();
        if (newTheme !== currentTheme.value) {
          currentTheme.value = newTheme;
          initEffects();
        }
      }
    });
  });

  observer.observe(document.body, {
    attributes: true
  });

  return observer;
}

// 动画循环
function animate(timestamp) {
  const canvas = canvasRef.value;
  if (!canvas) {
    console.warn('Canvas not available');
    return;
  }

  const ctx = canvas.getContext('2d');
  if (!ctx) {
    console.error('Failed to get 2D context');
    return;
  }

  const dpr = window.devicePixelRatio || 1;

  // 更新性能监控
  performanceMonitor.update(timestamp);

  // 动态调整性能级别
  const currentPerformanceLevel = performanceMonitor.getPerformanceLevel();
  if (currentPerformanceLevel !== config.value.performance) {
    config.value.performance = currentPerformanceLevel;
    parameterAdjuster.adjustByPerformanceLevel(currentPerformanceLevel);
    if (rendererOptimizer) {
      rendererOptimizer.optimizeRenderSettings(currentPerformanceLevel);
    }
  }

  ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr);

  if (config.value && config.value.effects) {
    const effectsToRender = config.value.performance === 'low'
      ? config.value.effects.slice(0, 1)
      : config.value.effects;

    effectsToRender.forEach((effectName) => {
      const effect = effects.value[effectName];
      if (effect) {
        try {
          const data = effect.update(canvas.width / dpr, canvas.height / dpr, timestamp);
          
          // 根据效果类型调用不同的渲染方法
          if (['risingWaveFlow', 'inkDiffusion', 'silkFlow'].includes(effectName)) {
            effect.render(ctx, data, canvas.width / dpr, canvas.height / dpr);
          } else {
            effect.render(ctx, data);
          }
        } catch (error) {
          console.error(`Error rendering effect ${effectName}:`, error);
        }
      } else {
        console.warn(`Effect not found: ${effectName}`);
      }
    });
  }

  animationId.value = requestAnimationFrame(animate);
}

// 节流函数
function throttle(func, delay) {
  let lastCall = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      return func(...args);
    }
  };
}

// 调整画布大小
const resizeCanvas = throttle(function () {
  const canvas = canvasRef.value;
  if (!canvas) return;

  const dpr = window.devicePixelRatio || 1;
  const width = window.innerWidth;
  const height = window.innerHeight;

  canvas.width = width * dpr;
  canvas.height = height * dpr;
  canvas.style.width = width + 'px';
  canvas.style.height = height + 'px';

  const ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.scale(dpr, dpr);
  }

  const container = canvas.parentElement;
  if (container) {
    container.style.width = width + 'px';
    container.style.height = height + 'px';
  }
}, 100);

// 生命周期钩子
onMounted(() => {
  // 初始化主题
  currentTheme.value = detectTheme();

  // 初始化效果
  initEffects();

  // 调整画布大小
  resizeCanvas();

  // 开始动画
  animationId.value = requestAnimationFrame(animate);

  // 监听窗口大小变化
  window.addEventListener('resize', resizeCanvas);

  // 监听主题变化
  const themeObserver = watchTheme();

  // 保存清理函数
  onUnmounted(() => {
    // 停止动画
    if (animationId.value) {
      cancelAnimationFrame(animationId.value);
    }

    // 移除事件监听
    window.removeEventListener('resize', resizeCanvas);

    // 停止主题观察
    themeObserver.disconnect();
  });
});

// 监听预设变化
watch(() => props.preset, () => {
  initEffects();
});

// 监听强度变化
watch(() => props.intensity, () => {
  initEffects();
});
</script>

<template>
  <div class="animation-background">
    <canvas ref="canvasRef" class="animation-canvas"></canvas>
  </div>
</template>

<style scoped>
.animation-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  overflow: hidden;
  pointer-events: none;
  margin: 0;
  padding: 0;
}

.animation-canvas {
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  margin: 0;
  padding: 0;
  border: none;
  outline: none;
}

:global(body) {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

@media (max-width: 768px) {
  .animation-background {
  }
}

:global(.dark-theme) .animation-background {
}
</style>
