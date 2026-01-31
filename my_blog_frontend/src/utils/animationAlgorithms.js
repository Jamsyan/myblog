/**
 * 动画算法库 - 实现粒子流、波浪涟漪和极光效果
 */

/**
 * 粒子流效果
 */
export class ParticleFlow {
  /**
   * 构造函数
   * @param {Object} options - 配置选项
   */
  constructor(options = {}) {
    this.maxParticles = options.maxParticles || 50;
    this.particleSize = options.particleSize || 2;
    this.speed = options.speed || 1;
    this.lifeTime = options.lifeTime || 100;
    this.colors = options.colors || ['#FFFFFF'];
    this.particles = [];
    this.initParticles();
  }

  /**
   * 初始化粒子
   */
  initParticles() {
    this.particles = [];
    for (let i = 0; i < this.maxParticles; i++) {
      this.particles.push(this.createParticle());
    }
  }

  /**
   * 创建单个粒子
   * @returns {Object} 粒子对象
   */
  createParticle() {
    return {
      x: 0,
      y: 0,
      vx: (Math.random() - 0.5) * this.speed,
      vy: (Math.random() - 0.5) * this.speed,
      opacity: Math.random() * 0.8 + 0.2,
      life: Math.random() * this.lifeTime,
      color: this.colors[Math.floor(Math.random() * this.colors.length)],
      size: Math.random() * this.particleSize + 1
    };
  }

  /**
   * 更新粒子状态
   * @param {number} width - 画布宽度
   * @param {number} height - 画布高度
   * @param {number} time - 时间戳
   * @returns {Array} 更新后的粒子数组
   */
  update(width, height, time) {
    this.particles.forEach((particle, index) => {
      // 更新位置
      particle.x += particle.vx;
      particle.y += particle.vy;

      // 边界检测
      if (particle.x < 0 || particle.x > width) {
        particle.vx *= -1;
      }
      if (particle.y < 0 || particle.y > height) {
        particle.vy *= -1;
      }

      // 更新生命周期
      particle.life -= 1;

      // 重置死亡粒子
      if (particle.life <= 0) {
        this.particles[index] = this.createParticle();
        this.particles[index].x = Math.random() * width;
        this.particles[index].y = Math.random() * height;
      }

      // 随时间变化透明度
      particle.opacity = Math.sin(time * 0.001 + index) * 0.4 + 0.6;
    });

    return this.particles;
  }

  /**
   * 设置颜色
   * @param {Array<string>} colors - 颜色数组
   */
  setColors(colors) {
    this.colors = colors;
  }

  /**
   * 渲染粒子
   * @param {CanvasRenderingContext2D} ctx - Canvas上下文
   * @param {Array} particles - 粒子数组
   */
  render(ctx, particles) {
    particles.forEach(particle => {
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      ctx.fillStyle = `${particle.color}${Math.floor(particle.opacity * 255).toString(16).padStart(2, '0')}`;
      ctx.fill();
    });
  }
}

/**
 * 波浪涟漪效果
 */
export class WaveRipple {
  /**
   * 构造函数
   * @param {Object} options - 配置选项
   */
  constructor(options = {}) {
    this.maxWaves = options.maxWaves || 5;
    this.waveSpeed = options.waveSpeed || 2;
    this.colors = options.colors || ['#0000FF'];
    this.waves = [];
    this.initWaves();
  }

  /**
   * 初始化波浪
   */
  initWaves() {
    this.waves = [];
    for (let i = 0; i < this.maxWaves; i++) {
      this.waves.push({
        radius: Math.random() * 100,
        speed: Math.random() * this.waveSpeed + 1,
        opacity: Math.random() * 0.5 + 0.1,
        color: this.colors[Math.floor(Math.random() * this.colors.length)],
        centerX: 0,
        centerY: 0
      });
    }
  }

  /**
   * 更新波浪状态
   * @param {number} width - 画布宽度
   * @param {number} height - 画布高度
   * @param {number} time - 时间戳
   * @returns {Array} 更新后的波浪数组
   */
  update(width, height, time) {
    this.waves.forEach((wave, index) => {
      // 设置中心位置
      wave.centerX = width / 2 + Math.sin(time * 0.001 + index) * 50;
      wave.centerY = height / 2 + Math.cos(time * 0.001 + index) * 50;

      // 更新半径
      wave.radius += wave.speed;

      // 更新透明度
      wave.opacity = Math.sin(time * 0.002 + index) * 0.2 + 0.3;

      // 重置过大的波浪
      if (wave.radius > Math.max(width, height)) {
        this.waves[index] = {
          radius: 0,
          speed: Math.random() * this.waveSpeed + 1,
          opacity: Math.random() * 0.5 + 0.1,
          color: this.colors[Math.floor(Math.random() * this.colors.length)],
          centerX: width / 2,
          centerY: height / 2
        };
      }
    });

    return this.waves;
  }

  /**
   * 设置颜色
   * @param {Array<string>} colors - 颜色数组
   */
  setColors(colors) {
    this.colors = colors;
  }

  /**
   * 渲染波浪
   * @param {CanvasRenderingContext2D} ctx - Canvas上下文
   * @param {Array} waves - 波浪数组
   */
  render(ctx, waves) {
    waves.forEach(wave => {
      ctx.beginPath();
      ctx.arc(wave.centerX, wave.centerY, wave.radius, 0, Math.PI * 2);
      ctx.strokeStyle = `${wave.color}${Math.floor(wave.opacity * 255).toString(16).padStart(2, '0')}`;
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  }
}

/**
 * 极光效果
 */
export class AuroraEffect {
  /**
   * 构造函数
   * @param {Object} options - 配置选项
   */
  constructor(options = {}) {
    this.segments = options.segments || 10;
    this.speed = options.speed || 0.5;
    this.colors = options.colors || ['#4A148C', '#7B1FA2', '#9C27B0'];
    this.waveHeight = options.waveHeight || 100;
    this.waveLength = options.waveLength || 200;
  }

  /**
   * 更新极光状态
   * @param {number} width - 画布宽度
   * @param {number} height - 画布高度
   * @param {number} time - 时间戳
   * @returns {Array} 更新后的极光段数组
   */
  update(width, height, time) {
    const segments = [];
    const segmentWidth = width / this.segments;

    for (let i = 0; i <= this.segments; i++) {
      const x = i * segmentWidth;
      const y = height / 2 + Math.sin(time * 0.001 * this.speed + x / this.waveLength) * this.waveHeight;

      segments.push({
        x,
        y,
        opacity: Math.sin(time * 0.002 + i) * 0.3 + 0.7,
        color: this.colors[Math.floor((i / this.segments) * this.colors.length)]
      });
    }

    return segments;
  }

  /**
   * 设置颜色
   * @param {Array<string>} colors - 颜色数组
   */
  setColors(colors) {
    this.colors = colors;
  }

  /**
   * 渲染极光
   * @param {CanvasRenderingContext2D} ctx - Canvas上下文
   * @param {Array} segments - 极光段数组
   * @param {number} width - 画布宽度
   * @param {number} height - 画布高度
   */
  render(ctx, segments, width, height) {
    if (!segments || segments.length === 0) return;

    const lastSegment = segments[segments.length - 1];

    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    this.colors.forEach((color, index) => {
      gradient.addColorStop(index / (this.colors.length - 1), color);
    });

    ctx.beginPath();
    ctx.moveTo(segments[0].x, segments[0].y);

    for (let i = 1; i < segments.length; i++) {
      const xc = (segments[i - 1].x + segments[i].x) / 2;
      const yc = (segments[i - 1].y + segments[i].y) / 2;
      ctx.quadraticCurveTo(segments[i - 1].x, segments[i - 1].y, xc, yc);
    }

    ctx.lineTo(lastSegment.x, lastSegment.y);
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();

    ctx.fillStyle = gradient;
    ctx.globalAlpha = 0.3;
    ctx.fill();
    ctx.globalAlpha = 1;

    ctx.beginPath();
    ctx.moveTo(segments[0].x, segments[0].y);

    for (let i = 1; i < segments.length; i++) {
      const xc = (segments[i - 1].x + segments[i].x) / 2;
      const yc = (segments[i - 1].y + segments[i].y) / 2;
      ctx.quadraticCurveTo(segments[i - 1].x, segments[i - 1].y, xc, yc);
    }

    ctx.lineTo(lastSegment.x, lastSegment.y);
    ctx.lineTo(width, 0);
    ctx.lineTo(0, 0);
    ctx.closePath();

    ctx.fillStyle = gradient;
    ctx.globalAlpha = 0.2;
    ctx.fill();
    ctx.globalAlpha = 1;
  }
}
