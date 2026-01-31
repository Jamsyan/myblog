/**
 * 动画配置文件 - 管理主题动画参数和预设
 */

/**
 * 动画配置对象
 */
export const animationConfig = {
  // 主题配置
  themes: {
    'theme-china-red': {
      name: '中国红',
      designPhilosophy: '生命力、活泼力、欣欣向荣',
      colors: {
        primary: '#C62828',
        secondary: '#E53935',
        animationColors: [
          { color: '#B71C1C', weight: 0.25 },
          { color: '#C62828', weight: 0.30 },
          { color: '#E53935', weight: 0.25 },
          { color: '#FFA726', weight: 0.10 },
          { color: '#FFCDD2', weight: 0.10 }
        ]
      },
      effects: {
        flameParticleFlow: {
          maxParticles: 200,
          maxLanterns: 6,
          maxFireworks: 3,
          maxClouds: 3,
          speed: 1.5,
          intensity: 'high'
        },
        risingWaveFlow: {
          maxWaves: 4,
          speed: 0.8,
          intensity: 'medium'
        },
        pulseGlow: {
          maxPulses: 3,
          speed: 0.5,
          intensity: 'high'
        }
      },
      themeEffects: ['flameParticleFlow', 'risingWaveFlow', 'pulseGlow'],
      animationIntensity: 'high'
    },
    'theme-danqing-blue': {
      name: '丹青蓝',
      designPhilosophy: '国风国画、国学水墨',
      colors: {
        primary: '#0D47A1',
        secondary: '#1976D2',
        animationColors: [
          { color: '#0A2463', weight: 0.25 },
          { color: '#0D47A1', weight: 0.30 },
          { color: '#42A5F5', weight: 0.25 },
          { color: '#00ACC1', weight: 0.10 },
          { color: '#E3F2FD', weight: 0.10 }
        ]
      },
      effects: {
        inkDiffusion: {
          maxInkSpots: 15,
          maxBambooLeaves: 20,
          maxClouds: 8,
          speed: 0.5,
          intensity: 'medium'
        },
        bambooLeaves: {
          maxLeaves: 20,
          speed: 0.8,
          intensity: 'medium'
        },
        cloudMist: {
          maxClouds: 8,
          speed: 0.4,
          intensity: 'low'
        }
      },
      themeEffects: ['inkDiffusion', 'bambooLeaves', 'cloudMist'],
      animationIntensity: 'low'
    },
    'theme-fenxia-purple': {
      name: '粉霞紫',
      designPhilosophy: '诱惑与色欲诱惑',
      colors: {
        primary: '#7B1FA2',
        secondary: '#9C27B0',
        animationColors: [
          { color: '#4A148C', weight: 0.25 },
          { color: '#7B1FA2', weight: 0.30 },
          { color: '#9C27B0', weight: 0.25 },
          { color: '#F06292', weight: 0.10 },
          { color: '#F3E5F5', weight: 0.10 }
        ]
      },
      effects: {
        silkFlow: {
          maxCurves: 10,
          maxMists: 15,
          speed: 0.5,
          intensity: 'medium'
        },
        breathingPulse: {
          maxOrbs: 10,
          speed: 0.02,
          intensity: 'medium'
        },
        mistEffect: {
          maxMists: 8,
          speed: 0.3,
          intensity: 'low'
        }
      },
      themeEffects: ['silkFlow', 'breathingPulse', 'mistEffect'],
      animationIntensity: 'medium'
    }
  },
  
  // 动画预设
  presets: {
    default: {
      name: '默认效果',
      effects: ['particleFlow'],
      intensity: 'medium'
    },
    flow: {
      name: '流动效果',
      effects: ['particleFlow', 'auroraEffect'],
      intensity: 'high'
    },
    sparkle: {
      name: '闪烁效果',
      effects: ['particleFlow', 'waveRipple'],
      intensity: 'medium'
    },
    calm: {
      name: '平静效果',
      effects: ['auroraEffect'],
      intensity: 'low'
    }
  },
  
  // 性能级别
  performance: {
    high: {
      pixelRatio: 2,
      frameRate: 60,
      particleDensity: 1.0
    },
    medium: {
      pixelRatio: 1.5,
      frameRate: 60,
      particleDensity: 0.7
    },
    low: {
      pixelRatio: 1,
      frameRate: 30,
      particleDensity: 0.4
    }
  }
};

/**
 * 获取主题配置
 * @param {string} themeName - 主题名称
 * @returns {Object} 主题配置对象
 */
export function getThemeConfig(themeName) {
  return animationConfig.themes[themeName] || animationConfig.themes['theme-china-red'];
}

/**
 * 获取预设配置
 * @param {string} presetName - 预设名称
 * @returns {Object} 预设配置对象
 */
export function getPreset(presetName) {
  return animationConfig.presets[presetName] || animationConfig.presets.default;
}

/**
 * 获取性能配置
 * @param {string} level - 性能级别
 * @returns {Object} 性能配置对象
 */
export function getPerformanceConfig(level) {
  return animationConfig.performance[level] || animationConfig.performance.medium;
}

/**
 * 验证动画参数
 * @param {Object} params - 输入参数
 * @param {Object} config - 配置对象
 * @returns {Object} 验证后的参数
 */
export function validateParams(params, config) {
  const validated = {};
  
  Object.keys(config).forEach(key => {
    const value = params[key];
    const configValue = config[key];
    
    if (typeof value === 'number') {
      // 确保值在合理范围内
      if (configValue.min !== undefined && value < configValue.min) {
        validated[key] = configValue.min;
      } else if (configValue.max !== undefined && value > configValue.max) {
        validated[key] = configValue.max;
      } else {
        validated[key] = value;
      }
    } else {
      validated[key] = value || configValue.default;
    }
  });
  
  return validated;
}

/**
 * 获取主题动画颜色数组
 * @param {string} themeName - 主题名称
 * @returns {Array<string>} 颜色数组
 */
export function getThemeAnimationColors(themeName) {
  const theme = getThemeConfig(themeName);
  
  // 防御性检查
  if (!theme || !theme.colors || !theme.colors.animationColors) {
    console.warn(`Invalid theme config for ${themeName}`);
    return ['#FF0000', '#00FF00', '#0000FF'];
  }
  
  // 过滤掉无效项并提取颜色
  const colors = theme.colors.animationColors
    .filter(item => item && typeof item.color === 'string')
    .map(item => item.color);
  
  // 如果过滤后没有颜色，返回默认颜色
  if (colors.length === 0) {
    console.warn(`No valid colors found for ${themeName}`);
    return ['#FF0000', '#00FF00', '#0000FF'];
  }
  
  return colors;
}

/**
 * 获取主题动画效果配置
 * @param {string} themeName - 主题名称
 * @param {string} effectName - 效果名称
 * @returns {Object} 效果配置
 */
export function getThemeEffectConfig(themeName, effectName) {
  const theme = getThemeConfig(themeName);
  return theme.effects[effectName] || {};
}

/**
 * 检测设备性能级别
 * @returns {string} 性能级别
 */
export function detectPerformanceLevel() {
  // 简单的性能检测
  const hasHighPerformance = (
    navigator.hardwareConcurrency >= 4 &&
    window.devicePixelRatio >= 1.5 &&
    typeof window.PerformanceObserver === 'function'
  );
  
  const hasLowPerformance = (
    navigator.hardwareConcurrency <= 2 ||
    window.devicePixelRatio < 1.2
  );
  
  if (hasHighPerformance) {
    return 'high';
  } else if (hasLowPerformance) {
    return 'low';
  } else {
    return 'medium';
  }
}

/**
 * 生成动画配置
 * @param {string} themeName - 主题名称
 * @param {string} presetName - 预设名称
 * @returns {Object} 完整动画配置
 */
export function generateAnimationConfig(themeName, presetName) {
  const theme = getThemeConfig(themeName);
  const preset = getPreset(presetName);
  const performanceLevel = detectPerformanceLevel();
  const performance = getPerformanceConfig(performanceLevel);
  
  // 使用主题专用效果，如果预设存在则使用预设效果
  const effects = theme.themeEffects || preset.effects;
  
  return {
    theme: themeName,
    preset: presetName,
    performance: performanceLevel,
    colors: getThemeAnimationColors(themeName),
    effects: effects,
    intensity: theme.animationIntensity || preset.intensity,
    performanceConfig: performance,
    themeConfig: theme,
    designPhilosophy: theme.designPhilosophy || ''
  };
}
