/**
 * 动画性能优化工具
 * 提供性能检测、动态调整和优化策略
 */

/**
 * 性能监控器
 */
export class PerformanceMonitor {
  constructor() {
    this.fps = 60;
    this.frameTime = 16.67;
    this.frames = 0;
    this.lastTime = performance.now();
    this.fpsHistory = [];
    this.maxHistoryLength = 60;
    this.performanceLevel = 'high';
  }

  /**
   * 更新性能数据
   * @param {number} timestamp - 当前时间戳
   */
  update(timestamp) {
    this.frames++;
    const currentTime = timestamp;
    const delta = currentTime - this.lastTime;

    if (delta >= 1000) {
      this.fps = Math.round((this.frames * 1000) / delta);
      this.frameTime = delta / this.frames;
      this.fpsHistory.push(this.fps);
      
      if (this.fpsHistory.length > this.maxHistoryLength) {
        this.fpsHistory.shift();
      }

      this.updatePerformanceLevel();
      
      this.frames = 0;
      this.lastTime = currentTime;
    }
  }

  /**
   * 更新性能级别
   */
  updatePerformanceLevel() {
    const avgFps = this.getAverageFps();
    
    if (avgFps >= 50) {
      this.performanceLevel = 'high';
    } else if (avgFps >= 30) {
      this.performanceLevel = 'medium';
    } else {
      this.performanceLevel = 'low';
    }
  }

  /**
   * 获取平均FPS
   * @returns {number} 平均FPS
   */
  getAverageFps() {
    if (this.fpsHistory.length === 0) return 60;
    const sum = this.fpsHistory.reduce((acc, fps) => acc + fps, 0);
    return Math.round(sum / this.fpsHistory.length);
  }

  /**
   * 获取当前性能级别
   * @returns {string} 性能级别
   */
  getPerformanceLevel() {
    return this.performanceLevel;
  }

  /**
   * 重置监控器
   */
  reset() {
    this.fps = 60;
    this.frameTime = 16.67;
    this.frames = 0;
    this.lastTime = performance.now();
    this.fpsHistory = [];
    this.performanceLevel = 'high';
  }
}

/**
 * 动态参数调整器
 */
export class DynamicParameterAdjuster {
  constructor() {
    this.adjustments = {
      particleDensity: 1.0,
      animationSpeed: 1.0,
      renderQuality: 1.0,
      effectCount: 1.0
    };
  }

  /**
   * 根据性能级别调整参数
   * @param {string} performanceLevel - 性能级别
   */
  adjustByPerformanceLevel(performanceLevel) {
    switch (performanceLevel) {
      case 'high':
        this.adjustments = {
          particleDensity: 1.0,
          animationSpeed: 1.0,
          renderQuality: 1.0,
          effectCount: 1.0
        };
        break;
      case 'medium':
        this.adjustments = {
          particleDensity: 0.7,
          animationSpeed: 0.9,
          renderQuality: 0.85,
          effectCount: 0.8
        };
        break;
      case 'low':
        this.adjustments = {
          particleDensity: 0.4,
          animationSpeed: 0.8,
          renderQuality: 0.7,
          effectCount: 0.6
        };
        break;
    }
  }

  /**
   * 调整粒子数量
   * @param {number} baseCount - 基础数量
   * @returns {number} 调整后的数量
   */
  adjustParticleCount(baseCount) {
    return Math.max(1, Math.round(baseCount * this.adjustments.particleDensity));
  }

  /**
   * 调整动画速度
   * @param {number} baseSpeed - 基础速度
   * @returns {number} 调整后的速度
   */
  adjustAnimationSpeed(baseSpeed) {
    return baseSpeed * this.adjustments.animationSpeed;
  }

  /**
   * 调整渲染质量
   * @param {number} baseQuality - 基础质量
   * @returns {number} 调整后的质量
   */
  adjustRenderQuality(baseQuality) {
    return baseQuality * this.adjustments.renderQuality;
  }

  /**
   * 调整效果数量
   * @param {number} baseCount - 基础数量
   * @returns {number} 调整后的数量
   */
  adjustEffectCount(baseCount) {
    return Math.max(1, Math.round(baseCount * this.adjustments.effectCount));
  }

  /**
   * 获取当前调整参数
   * @returns {Object} 调整参数
   */
  getAdjustments() {
    return { ...this.adjustments };
  }
}

/**
 * Canvas渲染优化器
 */
export class CanvasRendererOptimizer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.offscreenCanvas = null;
    this.offscreenCtx = null;
    this.cachedElements = new Map();
    this.useOffscreenCanvas = this.checkOffscreenCanvasSupport();
  }

  /**
   * 检查离屏Canvas支持
   * @returns {boolean} 是否支持
   */
  checkOffscreenCanvasSupport() {
    return typeof OffscreenCanvas !== 'undefined';
  }

  /**
   * 初始化离屏Canvas
   * @param {number} width - 宽度
   * @param {number} height - 高度
   */
  initOffscreenCanvas(width, height) {
    if (this.useOffscreenCanvas) {
      this.offscreenCanvas = new OffscreenCanvas(width, height);
      this.offscreenCtx = this.offscreenCanvas.getContext('2d');
    } else {
      this.offscreenCanvas = document.createElement('canvas');
      this.offscreenCanvas.width = width;
      this.offscreenCanvas.height = height;
      this.offscreenCtx = this.offscreenCanvas.getContext('2d');
    }
  }

  /**
   * 缓存静态元素
   * @param {string} key - 缓存键
   * @param {Function} renderFn - 渲染函数
   */
  cacheElement(key, renderFn) {
    if (!this.cachedElements.has(key)) {
      if (!this.offscreenCanvas) {
        this.initOffscreenCanvas(this.canvas.width, this.canvas.height);
      }
      
      this.offscreenCtx.clearRect(0, 0, this.offscreenCanvas.width, this.offscreenCanvas.height);
      renderFn(this.offscreenCtx);
      
      const imageData = this.offscreenCtx.getImageData(0, 0, this.offscreenCanvas.width, this.offscreenCanvas.height);
      this.cachedElements.set(key, imageData);
    }
  }

  /**
   * 绘制缓存元素
   * @param {string} key - 缓存键
   * @param {number} x - x坐标
   * @param {number} y - y坐标
   */
  drawCachedElement(key, x, y) {
    const imageData = this.cachedElements.get(key);
    if (imageData) {
      this.ctx.putImageData(imageData, x, y);
    }
  }

  /**
   * 清除缓存
   */
  clearCache() {
    this.cachedElements.clear();
  }

  /**
   * 优化渲染设置
   * @param {string} performanceLevel - 性能级别
   */
  optimizeRenderSettings(performanceLevel) {
    switch (performanceLevel) {
      case 'high':
        this.ctx.imageSmoothingEnabled = true;
        this.ctx.imageSmoothingQuality = 'high';
        break;
      case 'medium':
        this.ctx.imageSmoothingEnabled = true;
        this.ctx.imageSmoothingQuality = 'medium';
        break;
      case 'low':
        this.ctx.imageSmoothingEnabled = false;
        break;
    }
  }

  /**
   * 批量绘制优化
   * @param {Array} drawCommands - 绘制命令数组
   */
  batchDraw(drawCommands) {
    this.ctx.save();
    drawCommands.forEach(command => {
      this.ctx.beginPath();
      command(this.ctx);
    });
    this.ctx.restore();
  }

  /**
   * 视口裁剪优化
   * @param {number} x - x坐标
   * @param {number} y - y坐标
   * @param {number} width - 宽度
   * @param {number} height - 高度
   * @param {Function} renderFn - 渲染函数
   */
  clipAndRender(x, y, width, height, renderFn) {
    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.rect(x, y, width, height);
    this.ctx.clip();
    renderFn(this.ctx);
    this.ctx.restore();
  }
}

/**
 * 内存管理器
 */
export class AnimationMemoryManager {
  constructor() {
    this.pools = new Map();
    this.maxPoolSize = 100;
  }

  /**
   * 获取对象池
   * @param {string} type - 对象类型
   * @returns {Array} 对象池
   */
  getPool(type) {
    if (!this.pools.has(type)) {
      this.pools.set(type, []);
    }
    return this.pools.get(type);
  }

  /**
   * 从对象池获取对象
   * @param {string} type - 对象类型
   * @param {Function} factory - 工厂函数
   * @returns {Object} 对象
   */
  acquire(type, factory) {
    const pool = this.getPool(type);
    if (pool.length > 0) {
      return pool.pop();
    }
    return factory();
  }

  /**
   * 释放对象到对象池
   * @param {string} type - 对象类型
   * @param {Object} obj - 对象
   */
  release(type, obj) {
    const pool = this.getPool(type);
    if (pool.length < this.maxPoolSize) {
      pool.push(obj);
    }
  }

  /**
   * 清空对象池
   * @param {string} type - 对象类型
   */
  clearPool(type) {
    if (type) {
      this.pools.delete(type);
    } else {
      this.pools.clear();
    }
  }

  /**
   * 获取内存使用情况
   * @returns {Object} 内存使用信息
   */
  getMemoryUsage() {
    const usage = {};
    this.pools.forEach((pool, type) => {
      usage[type] = pool.length;
    });
    return usage;
  }
}

/**
 * 性能优化工具集合
 */
export const PerformanceUtils = {
  /**
   * 检测设备性能
   * @returns {Object} 性能信息
   */
  detectDevicePerformance() {
    const hardwareConcurrency = navigator.hardwareConcurrency || 4;
    const devicePixelRatio = window.devicePixelRatio || 1;
    const memory = navigator.deviceMemory || 4;
    
    let performanceLevel = 'medium';
    
    if (hardwareConcurrency >= 8 && devicePixelRatio >= 2 && memory >= 8) {
      performanceLevel = 'high';
    } else if (hardwareConcurrency <= 2 || devicePixelRatio < 1.2 || memory <= 2) {
      performanceLevel = 'low';
    }
    
    return {
      performanceLevel,
      hardwareConcurrency,
      devicePixelRatio,
      memory,
      hasWebGL: this.checkWebGLSupport(),
      hasOffscreenCanvas: typeof OffscreenCanvas !== 'undefined'
    };
  },

  /**
   * 检查WebGL支持
   * @returns {boolean} 是否支持
   */
  checkWebGLSupport() {
    try {
      const canvas = document.createElement('canvas');
      return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
    } catch (e) {
      return false;
    }
  },

  /**
   * 节流函数
   * @param {Function} func - 函数
   * @param {number} delay - 延迟
   * @returns {Function} 节流后的函数
   */
  throttle(func, delay) {
    let lastCall = 0;
    return function (...args) {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        return func.apply(this, args);
      }
    };
  },

  /**
   * 防抖函数
   * @param {Function} func - 函数
   * @param {number} delay - 延迟
   * @returns {Function} 防抖后的函数
   */
  debounce(func, delay) {
    let timeoutId;
    return function (...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  },

  /**
   * requestAnimationFrame的polyfill
   * @returns {Function} RAF函数
   */
  requestAnimationFramePolyfill() {
    return window.requestAnimationFrame ||
           window.webkitRequestAnimationFrame ||
           window.mozRequestAnimationFrame ||
           function (callback) {
             return window.setTimeout(callback, 1000 / 60);
           };
  },

  /**
   * cancelAnimationFrame的polyfill
   * @returns {Function} CAF函数
   */
  cancelAnimationFramePolyfill() {
    return window.cancelAnimationFrame ||
           window.webkitCancelAnimationFrame ||
           window.mozCancelAnimationFrame ||
           function (id) {
             return window.clearTimeout(id);
           };
  }
};
