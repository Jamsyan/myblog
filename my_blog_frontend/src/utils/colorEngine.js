/**
 * 颜色引擎 - 处理颜色转换、混合和主题色彩提取
 */
export class ColorEngine {
  /**
   * 将十六进制颜色转换为RGB对象
   * @param {string} hex - 十六进制颜色值
   * @returns {Object} RGB对象 {r, g, b}
   */
  static hexToRgb(hex) {
    // 移除#号
    hex = hex.replace(/^#/, '');
    
    // 处理简写形式
    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    
    const bigint = parseInt(hex, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    
    return { r, g, b };
  }

  /**
   * 将RGB值转换为十六进制颜色
   * @param {number} r - 红色通道值
   * @param {number} g - 绿色通道值
   * @param {number} b - 蓝色通道值
   * @returns {string} 十六进制颜色值
   */
  static rgbToHex(r, g, b) {
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toLowerCase();
  }

  /**
   * 将RGB值转换为HSL对象
   * @param {number} r - 红色通道值
   * @param {number} g - 绿色通道值
   * @param {number} b - 蓝色通道值
   * @returns {Object} HSL对象 {h, s, l}
   */
  static rgbToHsl(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;
    
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h = 0;
    let s = 0;
    const l = (max + min) / 2;
    
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
      }
      
      h /= 6;
    }
    
    return {
      h: Math.round(h * 360),
      s: Math.round(s * 100),
      l: Math.round(l * 100)
    };
  }

  /**
   * 将HSL值转换为RGB对象
   * @param {number} h - 色相
   * @param {number} s - 饱和度
   * @param {number} l - 亮度
   * @returns {Object} RGB对象 {r, g, b}
   */
  static hslToRgb(h, s, l) {
    h /= 360;
    s /= 100;
    l /= 100;
    
    let r, g, b;
    
    if (s === 0) {
      r = g = b = l; // 灰色
    } else {
      const hue2rgb = (p, q, t) => {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1/6) return p + (q - p) * 6 * t;
        if (t < 1/2) return q;
        if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
        return p;
      };
      
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      
      r = hue2rgb(p, q, h + 1/3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1/3);
    }
    
    return {
      r: Math.round(r * 255),
      g: Math.round(g * 255),
      b: Math.round(b * 255)
    };
  }

  /**
   * 混合多个颜色
   * @param {Array<string>} colors - 颜色数组
   * @param {Array<number>} weights - 权重数组
   * @returns {Object} 混合后的RGB对象
   */
  static blendColors(colors, weights) {
    const normalizedWeights = this.normalizeWeights(weights);
    
    let r = 0, g = 0, b = 0;
    
    colors.forEach((color, index) => {
      const rgb = this.hexToRgb(color);
      const weight = normalizedWeights[index];
      
      r += rgb.r * weight;
      g += rgb.g * weight;
      b += rgb.b * weight;
    });
    
    return {
      r: Math.round(r),
      g: Math.round(g),
      b: Math.round(b)
    };
  }

  /**
   * 归一化权重数组
   * @param {Array<number>} weights - 权重数组
   * @returns {Array<number>} 归一化后的权重数组
   */
  static normalizeWeights(weights) {
    const sum = weights.reduce((acc, weight) => acc + weight, 0);
    
    if (sum === 0) {
      return weights.map(() => 1 / weights.length);
    }
    
    return weights.map(weight => weight / sum);
  }

  /**
   * 从主题中提取颜色调色板
   * @param {Object} theme - 主题对象
   * @returns {Object} 颜色调色板
   */
  static getThemeColorPalette(theme) {
    if (!theme || !theme.colors) {
      return {
        primary: this.hexToRgb('#C62828'),
        secondary: this.hexToRgb('#E53935'),
        animationPalette: [
          this.hexToRgb('#C62828'),
          this.hexToRgb('#E53935'),
          this.hexToRgb('#FFCDD2')
        ]
      };
    }
    
    const { colors } = theme;
    
    return {
      primary: this.hexToRgb(colors.primary || '#C62828'),
      secondary: this.hexToRgb(colors.secondary || '#E53935'),
      animationPalette: (colors.animationColors || []).map(item => 
        this.hexToRgb(item.color || '#C62828')
      )
    };
  }

  /**
   * 根据主题获取动画颜色数组
   * @param {string} themeName - 主题名称
   * @returns {Array<string>} 动画颜色数组
   */
  static getAnimationColorsByTheme(themeName) {
    const themeColors = {
      'theme-china-red': [
        '#C62828',
        '#E53935',
        '#B71C1C',
        '#FFCDD2'
      ],
      'theme-danqing-blue': [
        '#0D47A1',
        '#1976D2',
        '#42A5F5',
        '#90CAF9'
      ],
      'theme-fenxia-purple': [
        '#7B1FA2',
        '#9C27B0',
        '#BA68C8',
        '#F3E5F5'
      ]
    };
    
    return themeColors[themeName] || themeColors['theme-china-red'];
  }

  /**
   * 生成渐变颜色数组
   * @param {string} startColor - 起始颜色
   * @param {string} endColor - 结束颜色
   * @param {number} steps - 步数
   * @returns {Array<string>} 渐变颜色数组
   */
  static generateGradient(startColor, endColor, steps) {
    const startRgb = this.hexToRgb(startColor);
    const endRgb = this.hexToRgb(endColor);
    const colors = [];
    
    for (let i = 0; i < steps; i++) {
      const ratio = i / (steps - 1);
      const r = Math.round(startRgb.r + (endRgb.r - startRgb.r) * ratio);
      const g = Math.round(startRgb.g + (endRgb.g - startRgb.g) * ratio);
      const b = Math.round(startRgb.b + (endRgb.b - startRgb.b) * ratio);
      
      colors.push(this.rgbToHex(r, g, b));
    }
    
    return colors;
  }

  /**
   * 生成主题专用颜色渐变
   * @param {string} themeName - 主题名称
   * @param {number} steps - 渐变步数
   * @returns {Array<string>} 渐变颜色数组
   */
  static generateThemeGradient(themeName, steps = 10) {
    const colors = this.getAnimationColorsByTheme(themeName);
    if (colors.length < 2) return colors;
    
    const gradientColors = [];
    const segments = colors.length - 1;
    const stepsPerSegment = Math.floor(steps / segments);
    
    for (let i = 0; i < segments; i++) {
      const segmentGradient = this.generateGradient(
        colors[i],
        colors[i + 1],
        stepsPerSegment + 1
      );
      gradientColors.push(...segmentGradient.slice(0, -1));
    }
    
    gradientColors.push(colors[colors.length - 1]);
    return gradientColors.slice(0, steps);
  }

  /**
   * 生成动态颜色（基于时间变化）
   * @param {string} themeName - 主题名称
   * @param {number} time - 时间戳
   * @param {number} index - 索引
   * @returns {string} 动态颜色
   */
  static generateDynamicColor(themeName, time, index = 0) {
    const colors = this.getAnimationColorsByTheme(themeName);
    const colorIndex = Math.floor((Math.sin(time * 0.001 + index) + 1) / 2 * (colors.length - 1));
    return colors[Math.min(colorIndex, colors.length - 1)];
  }

  /**
   * 生成主题透明度颜色数组
   * @param {string} themeName - 主题名称
   * @param {number} alpha - 透明度
   * @returns {Array<string>} 带透明度的颜色数组
   */
  static generateAlphaColors(themeName, alpha = 0.5) {
    const colors = this.getAnimationColorsByTheme(themeName);
    return colors.map(color => this.hexToRgba(color, alpha));
  }

  /**
   * 将十六进制颜色转换为RGBA
   * @param {string} hex - 十六进制颜色
   * @param {number} alpha - 透明度
   * @returns {string} RGBA颜色字符串
   */
  static hexToRgba(hex, alpha) {
    const rgb = this.hexToRgb(hex);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
  }

  /**
   * 调整颜色亮度
   * @param {string} hex - 十六进制颜色
   * @param {number} factor - 调整因子（-1到1）
   * @returns {string} 调整后的颜色
   */
  static adjustBrightness(hex, factor) {
    const hsl = this.rgbToHsl(...Object.values(this.hexToRgb(hex)));
    const newL = Math.max(0, Math.min(100, hsl.l + factor * 50));
    const rgb = this.hslToRgb(hsl.h, hsl.s, newL);
    return this.rgbToHex(rgb.r, rgb.g, rgb.b);
  }

  /**
   * 生成主题互补色
   * @param {string} themeName - 主题名称
   * @returns {Array<string>} 互补色数组
   */
  static generateComplementaryColors(themeName) {
    const colors = this.getAnimationColorsByTheme(themeName);
    return colors.map(color => {
      const hsl = this.rgbToHsl(...Object.values(this.hexToRgb(color)));
      const complementaryH = (hsl.h + 180) % 360;
      const rgb = this.hslToRgb(complementaryH, hsl.s, hsl.l);
      return this.rgbToHex(rgb.r, rgb.g, rgb.b);
    });
  }

  /**
   * 根据主题生成动画颜色数组（增强版）
   * @param {string} themeName - 主题名称
   * @param {number} count - 颜色数量
   * @returns {Array<string>} 动画颜色数组
   */
  static getEnhancedAnimationColors(themeName, count = 5) {
    const baseColors = this.getAnimationColorsByTheme(themeName);
    if (baseColors.length >= count) return baseColors.slice(0, count);
    
    const gradient = this.generateThemeGradient(themeName, count);
    return gradient;
  }
}
