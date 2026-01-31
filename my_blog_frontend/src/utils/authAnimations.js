import { ColorEngine } from './colorEngine.js';

/**
 * 登录页面 - 亚克力玻璃几何动画 + 物理坠落
 * 设计理念：亚克力透明磨砂玻璃效果，带触发动作
 * 特点：多色系搭配，物理坠落效果
 */
export class AcrylicGlassAnimation {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = canvas.width;
    this.height = canvas.height;

    this.size = options.size || 280;
    this.centerX = this.width / 2;
    this.centerY = this.height / 2;

    this.themeName = options.themeName || 'theme-china-red';
    this.colors = ColorEngine.getAnimationColorsByTheme(this.themeName);

    this.time = 0;
    this.shapes = [];
    this.isRunning = false;
    this.animationId = null;
    this.shouldFall = false;
    this.fallProgress = 0;

    this.initShapes();
  }

  getThemeColors() {
    const colorSchemes = {
      'theme-china-red': {
        primary: '#C62828',
        secondary: '#FFCDD2',
        neutral: '#FFFFFF',
        dark: '#8B0000'
      },
      'theme-danqing-blue': {
        primary: '#0D47A1',
        secondary: '#90CAF9',
        neutral: '#FFFFFF',
        dark: '#0A2463'
      },
      'theme-fenxia-purple': {
        primary: '#7B1FA2',
        secondary: '#F3E5F5',
        neutral: '#FFFFFF',
        dark: '#4A148C'
      }
    };
    return colorSchemes[this.themeName] || colorSchemes['theme-china-red'];
  }

  initShapes() {
    this.shapes = [];
    this.fragments = [];
    const shapeTypes = ['circle', 'triangle', 'square', 'hexagon', 'star'];
    const colors = this.getThemeColors();

    for (let i = 0; i < 18; i++) {
      const type = shapeTypes[i % shapeTypes.length];
      const colorIndex = Math.floor(Math.random() * 3);
      const color = [colors.primary, colors.secondary, colors.neutral, colors.dark][colorIndex];

      this.shapes.push({
        type: type,
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        size: 20 + Math.random() * 30,
        baseX: 0,
        baseY: 0,
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.03,
        floatSpeed: 0.6 + Math.random() * 0.6,
        floatPhase: Math.random() * Math.PI * 2,
        scale: 0.7 + Math.random() * 0.4,
        scalePhase: Math.random() * Math.PI * 2,
        vx: 0,
        vy: 0,
        alpha: 0.65 + Math.random() * 0.25,
        color: color,
        isFalling: false,
        hasShattered: false,
        shatterChance: Math.random() * 0.05
      });
    }

    this.shapes.forEach(shape => {
      shape.baseX = shape.x;
      shape.baseY = shape.y;
    });
  }

  setTheme(themeName) {
    this.themeName = themeName;
    this.colors = ColorEngine.getAnimationColorsByTheme(this.themeName);
  }

  resize(width, height) {
    this.width = width;
    this.height = height;
    this.centerX = width / 2;
    this.centerY = height / 2;
    this.canvas.width = width;
    this.canvas.height = height;
    this.initShapes();
  }

  triggerFall() {
    this.shouldFall = true;
    this.fallProgress = 0;

    this.shapes.forEach(shape => {
      shape.vx = (Math.random() - 0.5) * 4;
      shape.vy = 2 + Math.random() * 4;
      shape.isFalling = true;
    });
  }

  createFragments(shape) {
    const fragmentCount = 8 + Math.floor(Math.random() * 8);
    const fragments = [];

    for (let i = 0; i < fragmentCount; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 3 + Math.random() * 5;

      fragments.push({
        x: shape.x,
        y: shape.y,
        vx: Math.cos(angle) * speed + shape.vx * 0.5,
        vy: Math.sin(angle) * speed - Math.abs(shape.vy) * 0.6,
        size: shape.size * (0.12 + Math.random() * 0.18),
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.3,
        alpha: 0.9 + Math.random() * 0.1,
        color: shape.color,
        type: shape.type,
        decay: 0.015 + Math.random() * 0.015
      });
    }

    return fragments;
  }

  drawShape(shape) {
    const colors = this.getThemeColors();

    this.ctx.save();
    this.ctx.translate(shape.x, shape.y);
    this.ctx.rotate(shape.rotation);

    const gradient = this.ctx.createLinearGradient(-shape.size, -shape.size, shape.size, shape.size);
    gradient.addColorStop(0, this.hexToRgba(shape.color, 0.25));
    gradient.addColorStop(0.3, this.hexToRgba(shape.color, 0.4));
    gradient.addColorStop(0.7, this.hexToRgba(shape.color, 0.3));
    gradient.addColorStop(1, this.hexToRgba(shape.color, 0.15));

    const glassHighlight = this.ctx.createLinearGradient(-shape.size * 0.5, -shape.size * 0.5, shape.size * 0.5, shape.size * 0.5);
    glassHighlight.addColorStop(0, this.hexToRgba('#FFFFFF', 0.5));
    glassHighlight.addColorStop(0.5, this.hexToRgba('#FFFFFF', 0.2));
    glassHighlight.addColorStop(1, this.hexToRgba('#FFFFFF', 0));

    switch (shape.type) {
      case 'circle':
        this.ctx.beginPath();
        this.ctx.arc(0, 0, shape.size, 0, Math.PI * 2);
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        this.ctx.fillStyle = glassHighlight;
        this.ctx.fill();
        this.ctx.strokeStyle = this.hexToRgba('#FFFFFF', 0.6);
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        break;
      case 'triangle':
        this.ctx.beginPath();
        this.ctx.moveTo(0, -shape.size);
        this.ctx.lineTo(shape.size * 0.866, shape.size * 0.5);
        this.ctx.lineTo(-shape.size * 0.866, shape.size * 0.5);
        this.ctx.closePath();
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        this.ctx.fillStyle = glassHighlight;
        this.ctx.fill();
        this.ctx.strokeStyle = this.hexToRgba('#FFFFFF', 0.6);
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        break;
      case 'square':
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(-shape.size / 2, -shape.size / 2, shape.size, shape.size);
        this.ctx.fillStyle = glassHighlight;
        this.ctx.fillRect(-shape.size / 2, -shape.size / 2, shape.size, shape.size);
        this.ctx.strokeStyle = this.hexToRgba('#FFFFFF', 0.6);
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(-shape.size / 2, -shape.size / 2, shape.size, shape.size);
        break;
      case 'hexagon':
        this.ctx.beginPath();
        for (let i = 0; i < 6; i++) {
          const angle = (Math.PI * 2 / 6) * i - Math.PI / 2;
          const px = Math.cos(angle) * shape.size;
          const py = Math.sin(angle) * shape.size;
          if (i === 0) {
            this.ctx.moveTo(px, py);
          } else {
            this.ctx.lineTo(px, py);
          }
        }
        this.ctx.closePath();
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        this.ctx.fillStyle = glassHighlight;
        this.ctx.fill();
        this.ctx.strokeStyle = this.hexToRgba('#FFFFFF', 0.6);
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        break;
      case 'star':
        const points = 5;
        const outerRadius = shape.size;
        const innerRadius = shape.size * 0.4;
        this.ctx.beginPath();
        for (let i = 0; i < points * 2; i++) {
          const angle = (Math.PI / points) * i - Math.PI / 2;
          const radius = i % 2 === 0 ? outerRadius : innerRadius;
          const px = Math.cos(angle) * radius;
          const py = Math.sin(angle) * radius;
          if (i === 0) {
            this.ctx.moveTo(px, py);
          } else {
            this.ctx.lineTo(px, py);
          }
        }
        this.ctx.closePath();
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
        this.ctx.fillStyle = glassHighlight;
        this.ctx.fill();
        this.ctx.strokeStyle = this.hexToRgba('#FFFFFF', 0.6);
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        break;
    }

    this.ctx.restore();
  }

  updateShapes() {
    if (this.shouldFall) {
      this.fallProgress += 0.015;

      this.shapes.forEach(shape => {
        if (shape.isFalling && !shape.hasShattered) {
          shape.x += shape.vx;
          shape.y += shape.vy;
          shape.vy += 0.2;
          shape.rotation += shape.rotationSpeed;

          const midY = this.height * 0.75;
          const bottomY = this.height + 50;

          if (shape.y > midY && !shape.hasShattered && Math.random() < shape.shatterChance) {
            shape.hasShattered = true;
            const newFragments = this.createFragments(shape);
            this.fragments.push(...newFragments);
          } else if (shape.y > bottomY) {
            shape.hasShattered = true;
            const newFragments = this.createFragments(shape);
            this.fragments.push(...newFragments);
          }

          if (shape.hasShattered) {
            shape.alpha = Math.max(0, shape.alpha - 0.08);
          }
        }
      });

      this.fragments = this.fragments.filter(fragment => {
        fragment.x += fragment.vx;
        fragment.y += fragment.vy;
        fragment.vy += 0.15;
        fragment.rotation += fragment.rotationSpeed;
        fragment.alpha -= fragment.decay;

        return fragment.alpha > 0;
      });
    } else {
      this.shapes.forEach(shape => {
        shape.x = shape.baseX + Math.sin(this.time * 0.001 + shape.floatPhase) * 35;
        shape.y = shape.baseY + Math.cos(this.time * 0.001 + shape.floatPhase) * 25;
        shape.rotation += shape.rotationSpeed;
        shape.scale = 0.7 + Math.sin(this.time * 0.002 + shape.scalePhase) * 0.25;
      });
    }
  }

  hexToRgba(hex, alpha) {
    const rgb = ColorEngine.hexToRgb(hex);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    this.updateShapes();

    this.shapes.forEach(shape => {
      if (!shape.hasShattered || shape.alpha > 0) {
        this.ctx.save();
        this.ctx.globalAlpha = shape.alpha;
        this.drawShape(shape);
        this.ctx.restore();
      }
    });

    this.fragments.forEach(fragment => {
      this.ctx.save();
      this.ctx.globalAlpha = fragment.alpha;
      this.drawShape(fragment);
      this.ctx.restore();
    });

    this.time += 16;
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;

    const animate = () => {
      if (!this.isRunning) return;
      this.render();
      this.animationId = requestAnimationFrame(animate);
    };

    animate();
  }

  stop() {
    this.isRunning = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  destroy() {
    this.stop();
    this.shapes = [];
    this.fragments = [];
  }
}

/**
 * 注册页面 Step 1 - 能量漩涡动画
 * 设计理念：中心能量漩涡，多层旋转光环，能量粒子扩散
 * 特点：漩涡效果，能量爆发，拖尾效果
 */
export class FlowLightAnimation {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = canvas.width;
    this.height = canvas.height;

    this.size = options.size || 300;
    this.centerX = this.width / 2;
    this.centerY = this.height / 2;

    this.themeName = options.themeName || 'theme-china-red';
    this.colors = ColorEngine.getAnimationColorsByTheme(this.themeName);

    this.time = 0;
    this.rings = [];
    this.particles = [];
    this.isRunning = false;
    this.animationId = null;
    this.isPlaying = false;

    this.initRings();
    this.initParticles();
  }

  initRings() {
    this.rings = [];
    const ringCount = 8;

    for (let i = 0; i < ringCount; i++) {
      const baseRadius = 30 + i * 25;
      const colorIndex = i % this.colors.length;

      this.rings.push({
        radius: baseRadius,
        baseRadius: baseRadius,
        width: 3 + Math.random() * 4,
        alpha: 0.4 + Math.random() * 0.3,
        color: this.colors[colorIndex],
        rotationSpeed: (i % 2 === 0 ? 1 : -1) * (0.01 + Math.random() * 0.02),
        rotation: Math.random() * Math.PI * 2,
        segments: 8 + Math.floor(Math.random() * 8),
        gapSize: 0.2 + Math.random() * 0.3,
        pulsePhase: Math.random() * Math.PI * 2
      });
    }
  }

  initParticles() {
    this.particles = [];
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
      const angle = Math.random() * Math.PI * 2;
      const distance = 20 + Math.random() * 150;

      this.particles.push({
        angle: angle,
        distance: distance,
        baseDistance: distance,
        size: 2 + Math.random() * 4,
        alpha: 0.5 + Math.random() * 0.4,
        color: this.colors[Math.floor(Math.random() * this.colors.length)],
        speed: 0.5 + Math.random() * 1.5,
        rotationSpeed: (Math.random() - 0.5) * 0.02,
        trailLength: 5 + Math.floor(Math.random() * 10),
        trail: [],
        phase: Math.random() * Math.PI * 2
      });
    }
  }

  setTheme(themeName) {
    this.themeName = themeName;
    this.colors = ColorEngine.getAnimationColorsByTheme(this.themeName);
  }

  resize(width, height) {
    this.width = width;
    this.height = height;
    this.centerX = width / 2;
    this.centerY = height / 2;
    this.canvas.width = width;
    this.canvas.height = height;
    this.initRings();
  }

  play() {
    this.isPlaying = true;
    this.time = 0;
    this.initStrands();
    this.initBasePairs();
    this.initGrid();
    this.initDataStreams();
    this.initThemeEffects();
  }

  reset() {
    this.isPlaying = false;
    this.time = 0;
    this.initRings();
  }

  drawCore() {
    const coreSize = this.size * 0.12;
    const pulse = 1 + Math.sin(this.time * 0.005) * 0.2;

    const gradient = this.ctx.createRadialGradient(
      this.centerX, this.centerY, 0,
      this.centerX, this.centerY, coreSize * pulse
    );

    gradient.addColorStop(0, this.hexToRgba(this.colors[0], 1));
    gradient.addColorStop(0.3, this.hexToRgba(this.colors[1], 0.8));
    gradient.addColorStop(0.6, this.hexToRgba(this.colors[0], 0.5));
    gradient.addColorStop(1, this.hexToRgba(this.colors[0], 0));

    this.ctx.fillStyle = gradient;
    this.ctx.beginPath();
    this.ctx.arc(this.centerX, this.centerY, coreSize * pulse, 0, Math.PI * 2);
    this.ctx.fill();

    const innerGlow = this.ctx.createRadialGradient(
      this.centerX, this.centerY, 0,
      this.centerX, this.centerY, coreSize * pulse * 1.5
    );

    innerGlow.addColorStop(0, this.hexToRgba('#FFFFFF', 0.3));
    innerGlow.addColorStop(1, this.hexToRgba('#FFFFFF', 0));

    this.ctx.fillStyle = innerGlow;
    this.ctx.beginPath();
    this.ctx.arc(this.centerX, this.centerY, coreSize * pulse * 1.5, 0, Math.PI * 2);
    this.ctx.fill();
  }

  drawRings() {
    this.rings.forEach(ring => {
      ring.rotation += ring.rotationSpeed;
      const pulse = 1 + Math.sin(this.time * 0.003 + ring.pulsePhase) * 0.15;
      const currentRadius = ring.baseRadius * pulse;

      this.ctx.save();
      this.ctx.translate(this.centerX, this.centerY);
      this.ctx.rotate(ring.rotation);

      this.ctx.strokeStyle = this.hexToRgba(ring.color, ring.alpha);
      this.ctx.lineWidth = ring.width;
      this.ctx.lineCap = 'round';

      const segmentAngle = (Math.PI * 2) / ring.segments;
      const gapAngle = segmentAngle * ring.gapSize;

      for (let i = 0; i < ring.segments; i++) {
        const startAngle = i * segmentAngle;
        const endAngle = startAngle + segmentAngle - gapAngle;

        this.ctx.beginPath();
        this.ctx.arc(0, 0, currentRadius, startAngle, endAngle);
        this.ctx.stroke();
      }

      this.ctx.restore();
    });
  }

  drawParticles() {
    this.particles.forEach(particle => {
      particle.angle += particle.rotationSpeed;
      particle.distance += particle.speed;

      if (particle.distance > this.size * 0.6) {
        particle.distance = 20 + Math.random() * 30;
        particle.trail = [];
      }

      const x = this.centerX + Math.cos(particle.angle) * particle.distance;
      const y = this.centerY + Math.sin(particle.angle) * particle.distance;

      particle.trail.unshift({ x, y, alpha: particle.alpha });
      if (particle.trail.length > particle.trailLength) {
        particle.trail.pop();
      }

      const twinkle = 0.6 + Math.sin(particle.phase + this.time * 0.006) * 0.4;

      for (let i = particle.trail.length - 1; i >= 0; i--) {
        const trailPoint = particle.trail[i];
        const trailAlpha = trailPoint.alpha * (1 - i / particle.trail.length) * twinkle * 0.6;
        const trailSize = particle.size * (1 - i / particle.trail.length * 0.5);

        this.ctx.fillStyle = this.hexToRgba(particle.color, trailAlpha);
        this.ctx.beginPath();
        this.ctx.arc(trailPoint.x, trailPoint.y, trailSize, 0, Math.PI * 2);
        this.ctx.fill();
      }

      this.ctx.fillStyle = this.hexToRgba(particle.color, particle.alpha * twinkle);
      this.ctx.beginPath();
      this.ctx.arc(x, y, particle.size, 0, Math.PI * 2);
      this.ctx.fill();

      const glowSize = particle.size * 3;
      const glowGradient = this.ctx.createRadialGradient(x, y, 0, x, y, glowSize);
      glowGradient.addColorStop(0, this.hexToRgba(particle.color, particle.alpha * twinkle * 0.4));
      glowGradient.addColorStop(1, this.hexToRgba(particle.color, 0));
      this.ctx.fillStyle = glowGradient;
      this.ctx.beginPath();
      this.ctx.arc(x, y, glowSize, 0, Math.PI * 2);
      this.ctx.fill();
    });
  }

  hexToRgba(hex, alpha) {
    const rgb = ColorEngine.hexToRgb(hex);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    this.drawParticles();
    this.drawRings();
    this.drawCore();

    if (this.isPlaying) {
      this.time += 16;
    }
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;

    const animate = () => {
      if (!this.isRunning) return;
      this.render();
      this.animationId = requestAnimationFrame(animate);
    };

    animate();
  }

  stop() {
    this.isRunning = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  destroy() {
    this.stop();
    this.rings = [];
    this.particles = [];
  }
}

/**
 * 注册页面 Step 2 - 网点几何动画
 * 设计理念：网点矩阵效果，保持原有的好看设计
 * 特点：网格点阵，呼吸效果，轻微闪烁
 */
export class GeometryMatrixAnimation {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = canvas.width;
    this.height = canvas.height;

    this.size = options.size || 300;
    this.centerX = this.width / 2;
    this.centerY = this.height / 2;

    this.themeName = options.themeName || 'theme-china-red';
    this.colors = ColorEngine.getAnimationColorsByTheme(this.themeName);

    this.time = 0;
    this.dots = [];
    this.isRunning = false;
    this.animationId = null;
    this.isPlaying = false;

    this.initDots();
  }

  initDots() {
    this.dots = [];
    const gridSize = 10;
    const spacing = this.size / (gridSize + 1);

    for (let i = 1; i <= gridSize; i++) {
      for (let j = 1; j <= gridSize; j++) {
        const baseX = this.centerX - this.size / 2 + i * spacing;
        const baseY = this.centerY - this.size / 2 + j * spacing;

        this.dots.push({
          x: baseX,
          y: baseY,
          baseX: baseX,
          baseY: baseY,
          baseSize: 3 + Math.random() * 4,
          size: 3 + Math.random() * 4,
          color: this.colors[Math.floor(Math.random() * this.colors.length)],
          phase: Math.random() * Math.PI * 2,
          speed: 0.02 + Math.random() * 0.03,
          offsetX: (Math.random() - 0.5) * 8,
          offsetY: (Math.random() - 0.5) * 8,
          movePhase: Math.random() * Math.PI * 2,
          moveSpeed: 0.001 + Math.random() * 0.002,
          colorPhase: Math.random() * Math.PI * 2,
          colorSpeed: 0.002 + Math.random() * 0.003,
          twinklePhase: Math.random() * Math.PI * 2,
          twinkleSpeed: 0.003 + Math.random() * 0.005
        });
      }
    }
  }

  drawDots() {
    this.dots.forEach(dot => {
      const breathing = Math.sin(this.time * dot.speed + dot.phase) * 0.5 + 0.5;
      const moveX = Math.sin(this.time * dot.moveSpeed + dot.movePhase) * dot.offsetX;
      const moveY = Math.cos(this.time * dot.moveSpeed + dot.movePhase) * dot.offsetY;
      const twinkle = Math.sin(this.time * dot.twinkleSpeed + dot.twinklePhase) * 0.5 + 0.5;

      dot.x = dot.baseX + moveX;
      dot.y = dot.baseY + moveY;
      dot.size = dot.baseSize * (0.7 + breathing * 0.5);

      const colorIndex = Math.floor((Math.sin(this.time * dot.colorSpeed + dot.colorPhase) + 1) * this.colors.length / 2) % this.colors.length;
      const currentColor = this.colors[colorIndex];

      const alpha = (0.5 + breathing * 0.4) * (0.6 + twinkle * 0.4);

      this.ctx.beginPath();
      this.ctx.arc(dot.x, dot.y, dot.size, 0, Math.PI * 2);
      this.ctx.fillStyle = this.hexToRgba(currentColor, alpha);
      this.ctx.fill();

      const glowSize = dot.size * 2.5;
      const gradient = this.ctx.createRadialGradient(dot.x, dot.y, 0, dot.x, dot.y, glowSize);
      gradient.addColorStop(0, this.hexToRgba(currentColor, alpha * 0.4));
      gradient.addColorStop(1, this.hexToRgba(currentColor, 0));
      this.ctx.beginPath();
      this.ctx.arc(dot.x, dot.y, glowSize, 0, Math.PI * 2);
      this.ctx.fillStyle = gradient;
      this.ctx.fill();
    });
  }

  drawConnections() {
    const maxDistance = this.size / 7;

    for (let i = 0; i < this.dots.length; i++) {
      for (let j = i + 1; j < this.dots.length; j++) {
        const dx = this.dots[i].x - this.dots[j].x;
        const dy = this.dots[i].y - this.dots[j].y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < maxDistance) {
          const baseAlpha = (1 - distance / maxDistance) * 0.25;
          const pulse = Math.sin(this.time * 0.002 + i * 0.1 + j * 0.1) * 0.5 + 0.5;
          const alpha = baseAlpha * (0.5 + pulse * 0.5);

          const colorIndex = Math.floor((i + j) % this.colors.length);
          const lineColor = this.colors[colorIndex];

          this.ctx.beginPath();
          this.ctx.moveTo(this.dots[i].x, this.dots[i].y);
          this.ctx.lineTo(this.dots[j].x, this.dots[j].y);
          this.ctx.strokeStyle = this.hexToRgba(lineColor, alpha);
          this.ctx.lineWidth = 1 + pulse * 0.5;
          this.ctx.stroke();
        }
      }
    }
  }

  hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    this.drawConnections();
    this.drawDots();

    this.time += 1;
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;

    const animate = () => {
      if (!this.isRunning) return;
      this.render();
      this.animationId = requestAnimationFrame(animate);
    };

    animate();
  }

  play() {
    this.isPlaying = true;
  }

  stop() {
    this.isRunning = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  resize(width, height) {
    this.width = width;
    this.height = height;
    this.centerX = width / 2;
    this.centerY = height / 2;
    this.initDots();
  }

  destroy() {
    this.stop();
    this.dots = [];
  }
}

/**
 * 注册页面 Step 3 - DNA双螺旋动画
 * 设计理念：条带式DNA双螺旋，斜向布局，科技感背景
 * 特点：丝滑条带、斜向旋转、科技网格背景
 */
export class AtlantisRedFlashAnimation {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = canvas.width;
    this.height = canvas.height;

    this.size = options.size || 320;
    this.centerX = this.width / 2;
    this.centerY = this.height / 2;

    this.themeName = options.themeName || 'theme-china-red';
    this.colors = ColorEngine.getAnimationColorsByTheme(this.themeName);

    this.time = 0;
    this.strands = [];
    this.basePairs = [];
    this.gridCells = [];
    this.dataStreams = [];
    this.themeEffects = [];
    this.isRunning = false;
    this.animationId = null;
    this.isPlaying = false;

    this.initStrands();
    this.initBasePairs();
    this.initGrid();
    this.initDataStreams();
    this.initThemeEffects();
  }

  initStrands() {
    this.strands = [];
    const strandCount = 3;
    const pointCount = 60;
    const amplitude = 50;

    for (let s = 0; s < strandCount; s++) {
      const points = [];

      for (let i = 0; i <= pointCount; i++) {
        const t = i / pointCount;
        const y = (t - 0.5) * this.size * 0.8;
        const phase = Math.PI * 2 * t + s * Math.PI;

        points.push({
          t: t,
          y: y,
          phase: phase,
          amplitude: amplitude,
          texturePhase: Math.random() * Math.PI * 2
        });
      }

      this.strands.push({
        points: points,
        color: this.colors[s % this.colors.length],
        width: 5 + Math.random() * 2,
        shadowColor: this.colors[(s + 1) % this.colors.length],
        glowColor: this.colors[s % this.colors.length]
      });
    }
  }

  initBasePairs() {
    this.basePairs = [];
    const pairCount = 25;

    for (let i = 0; i < pairCount; i++) {
      const t = i / (pairCount - 1);
      const y = (t - 0.5) * this.size * 0.8;

      this.basePairs.push({
        y: y,
        phase: Math.PI * 2 * t,
        amplitude: 50,
        width: 3 + Math.random() * 2,
        color: this.colors[Math.floor(Math.random() * this.colors.length)]
      });
    }
  }

  initGrid() {
    this.gridCells = [];
    const gridSize = 12;
    const cellSize = this.size / gridSize;

    for (let i = 0; i < gridSize; i++) {
      for (let j = 0; j < gridSize; j++) {
        const x = this.centerX - this.size / 2 + i * cellSize + cellSize / 2;
        const y = this.centerY - this.size / 2 + j * cellSize + cellSize / 2;

        this.gridCells.push({
          x: x,
          y: y,
          size: cellSize * 0.8,
          alpha: 0.05 + Math.random() * 0.1,
          phase: Math.random() * Math.PI * 2,
          speed: 0.002 + Math.random() * 0.003,
          type: Math.random() < 0.3 ? 'hexagon' : 'square'
        });
      }
    }
  }

  initDataStreams() {
    this.dataStreams = [];
    const streamCount = 5;

    for (let i = 0; i < streamCount; i++) {
      const startX = this.centerX - this.size / 2 + Math.random() * this.size;
      const startY = this.centerY - this.size / 2 + Math.random() * this.size;

      this.dataStreams.push({
        x: startX,
        y: startY,
        targetX: startX + (Math.random() - 0.5) * 100,
        targetY: startY + (Math.random() - 0.5) * 100,
        speed: 0.5 + Math.random() * 0.5,
        progress: 0,
        alpha: 0.1 + Math.random() * 0.1,
        color: this.colors[Math.floor(Math.random() * this.colors.length)]
      });
    }
  }

  initThemeEffects() {
    this.themeEffects = [];
    const themeType = this.getThemeType();

    if (themeType === 'red') {
      this.initBloodEffects();
    } else if (themeType === 'blue') {
      this.initMistEffects();
    } else if (themeType === 'purple') {
      this.initCloudEffects();
    }
  }

  getThemeType() {
    if (this.themeName === 'theme-china-red') {
      return 'red';
    } else if (this.themeName === 'theme-danqing-blue') {
      return 'blue';
    } else if (this.themeName === 'theme-fenxia-purple') {
      return 'purple';
    }
    return 'red';
  }

  initBloodEffects() {
    const bloodDropCount = 15;

    for (let i = 0; i < bloodDropCount; i++) {
      const strandIndex = Math.floor(Math.random() * 3);
      const pointIndex = Math.floor(Math.random() * 60);
      const strand = this.strands[strandIndex];
      const point = strand.points[pointIndex];

      this.themeEffects.push({
        type: 'blood',
        x: point ? this.centerX + Math.sin(point.phase) * point.amplitude : this.centerX,
        y: point ? point.y : this.centerY,
        size: 3 + Math.random() * 4,
        alpha: 0.6 + Math.random() * 0.3,
        vy: 1 + Math.random() * 2,
        vx: (Math.random() - 0.5) * 0.5,
        trail: [],
        trailLength: 5 + Math.floor(Math.random() * 4),
        decay: 0.01 + Math.random() * 0.01,
        delay: Math.random() * 2000
      });
    }
  }

  initMistEffects() {
    const mistCount = 20;

    for (let i = 0; i < mistCount; i++) {
      const angle = Math.random() * Math.PI * 2;
      const distance = 60 + Math.random() * 80;

      this.themeEffects.push({
        type: 'mist',
        x: this.centerX + Math.cos(angle) * distance,
        y: this.centerY + Math.sin(angle) * distance,
        baseX: this.centerX + Math.cos(angle) * distance,
        baseY: this.centerY + Math.sin(angle) * distance,
        size: 40 + Math.random() * 40,
        alpha: 0.1 + Math.random() * 0.15,
        phase: Math.random() * Math.PI * 2,
        speed: 0.001 + Math.random() * 0.002,
        flowPhase: Math.random() * Math.PI * 2,
        flowSpeed: 0.002 + Math.random() * 0.002
      });
    }
  }

  initCloudEffects() {
    const cloudCount = 12;

    for (let i = 0; i < cloudCount; i++) {
      const angle = Math.random() * Math.PI * 2;
      const distance = 50 + Math.random() * 100;

      this.themeEffects.push({
        type: 'cloud',
        x: this.centerX + Math.cos(angle) * distance,
        y: this.centerY + Math.sin(angle) * distance,
        baseX: this.centerX + Math.cos(angle) * distance,
        baseY: this.centerY + Math.sin(angle) * distance,
        size: 50 + Math.random() * 50,
        alpha: 0.08 + Math.random() * 0.12,
        phase: Math.random() * Math.PI * 2,
        speed: 0.0008 + Math.random() * 0.001,
        curlPhase: Math.random() * Math.PI * 2,
        curlSpeed: 0.001 + Math.random() * 0.002
      });
    }
  }

  setTheme(themeName) {
    this.themeName = themeName;
    this.colors = ColorEngine.getAnimationColorsByTheme(this.themeName);
  }

  resize(width, height) {
    this.width = width;
    this.height = height;
    this.centerX = width / 2;
    this.centerY = height / 2;
    this.canvas.width = width;
    this.canvas.height = height;
    this.initStrands();
    this.initBasePairs();
    this.initGrid();
    this.initDataStreams();
    this.initThemeEffects();
  }

  play() {
    this.isPlaying = true;
    this.time = 0;
  }

  reset() {
    this.isPlaying = false;
    this.time = 0;
    this.initStrands();
    this.initBasePairs();
    this.initGrid();
    this.initDataStreams();
    this.initThemeEffects();
  }

  drawGrid() {
    this.gridCells.forEach(cell => {
      const twinkle = Math.sin(this.time * cell.speed + cell.phase) * 0.5 + 0.5;
      const alpha = cell.alpha * (0.3 + twinkle * 0.7);

      this.ctx.save();
      this.ctx.translate(cell.x, cell.y);

      this.ctx.fillStyle = this.hexToRgba(this.colors[0], alpha);

      if (cell.type === 'hexagon') {
        this.ctx.beginPath();
        for (let i = 0; i < 6; i++) {
          const angle = (Math.PI * 2 / 6) * i - Math.PI / 2;
          const px = Math.cos(angle) * cell.size / 2;
          const py = Math.sin(angle) * cell.size / 2;
          if (i === 0) {
            this.ctx.moveTo(px, py);
          } else {
            this.ctx.lineTo(px, py);
          }
        }
        this.ctx.closePath();
        this.ctx.fill();
      } else {
        this.ctx.fillRect(-cell.size / 2, -cell.size / 2, cell.size, cell.size);
      }

      this.ctx.restore();
    });
  }

  drawDataStreams() {
    this.dataStreams.forEach(stream => {
      stream.progress += stream.speed * 0.01;

      if (stream.progress >= 1) {
        stream.progress = 0;
        stream.x = this.centerX - this.size / 2 + Math.random() * this.size;
        stream.y = this.centerY - this.size / 2 + Math.random() * this.size;
        stream.targetX = stream.x + (Math.random() - 0.5) * 100;
        stream.targetY = stream.y + (Math.random() - 0.5) * 100;
      }

      const currentX = stream.x + (stream.targetX - stream.x) * stream.progress;
      const currentY = stream.y + (stream.targetY - stream.y) * stream.progress;

      const gradient = this.ctx.createLinearGradient(stream.x, stream.y, currentX, currentY);
      gradient.addColorStop(0, this.hexToRgba(stream.color, 0));
      gradient.addColorStop(0.5, this.hexToRgba(stream.color, stream.alpha));
      gradient.addColorStop(1, this.hexToRgba(stream.color, 0));

      this.ctx.strokeStyle = gradient;
      this.ctx.lineWidth = 1;
      this.ctx.lineCap = 'round';
      this.ctx.beginPath();
      this.ctx.moveTo(stream.x, stream.y);
      this.ctx.lineTo(currentX, currentY);
      this.ctx.stroke();
    });
  }

  drawThemeEffects() {
    this.themeEffects.forEach(effect => {
      if (effect.type === 'blood') {
        this.drawBloodEffect(effect);
      } else if (effect.type === 'mist') {
        this.drawMistEffect(effect);
      } else if (effect.type === 'cloud') {
        this.drawCloudEffect(effect);
      }
    });
  }

  drawBloodEffect(effect) {
    if (this.time < effect.delay) return;

    effect.x += effect.vx;
    effect.y += effect.vy;
    effect.vy += 0.08;
    effect.alpha -= effect.decay;

    effect.trail.unshift({ x: effect.x, y: effect.y, alpha: effect.alpha });
    if (effect.trail.length > effect.trailLength) {
      effect.trail.pop();
    }

    for (let i = effect.trail.length - 1; i >= 0; i--) {
      const trailPoint = effect.trail[i];
      const trailAlpha = trailPoint.alpha * (1 - i / effect.trail.length) * 0.5;
      const trailSize = effect.size * (1 - i / effect.trail.length * 0.3);

      this.ctx.fillStyle = this.hexToRgba(this.colors[0], trailAlpha);
      this.ctx.beginPath();
      this.ctx.arc(trailPoint.x, trailPoint.y, trailSize, 0, Math.PI * 2);
      this.ctx.fill();
    }

    this.ctx.fillStyle = this.hexToRgba(this.colors[0], effect.alpha);
    this.ctx.beginPath();
    this.ctx.arc(effect.x, effect.y, effect.size, 0, Math.PI * 2);
    this.ctx.fill();

    const glowSize = effect.size * 2;
    const gradient = this.ctx.createRadialGradient(effect.x, effect.y, 0, effect.x, effect.y, glowSize);
    gradient.addColorStop(0, this.hexToRgba(this.colors[0], effect.alpha * 0.5));
    gradient.addColorStop(1, this.hexToRgba(this.colors[0], 0));
    this.ctx.fillStyle = gradient;
    this.ctx.beginPath();
    this.ctx.arc(effect.x, effect.y, glowSize, 0, Math.PI * 2);
    this.ctx.fill();
  }

  drawMistEffect(effect) {
    const flowX = Math.cos(this.time * effect.flowSpeed + effect.flowPhase) * 15;
    const flowY = Math.sin(this.time * effect.flowSpeed + effect.flowPhase) * 15;
    const pulse = Math.sin(this.time * effect.speed + effect.phase) * 0.5 + 0.5;

    const x = effect.baseX + flowX;
    const y = effect.baseY + flowY;
    const alpha = effect.alpha * pulse;

    const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, effect.size);
    gradient.addColorStop(0, this.hexToRgba(this.colors[1], alpha * 0.8));
    gradient.addColorStop(0.5, this.hexToRgba(this.colors[1], alpha * 0.4));
    gradient.addColorStop(1, this.hexToRgba(this.colors[1], 0));

    this.ctx.fillStyle = gradient;
    this.ctx.beginPath();
    this.ctx.arc(x, y, effect.size, 0, Math.PI * 2);
    this.ctx.fill();

    const glowSize = effect.size * 1.5;
    const glowGradient = this.ctx.createRadialGradient(x, y, 0, x, y, glowSize);
    glowGradient.addColorStop(0, this.hexToRgba(this.colors[1], alpha * 0.3));
    glowGradient.addColorStop(1, this.hexToRgba(this.colors[1], 0));
    this.ctx.fillStyle = glowGradient;
    this.ctx.beginPath();
    this.ctx.arc(x, y, glowSize, 0, Math.PI * 2);
    this.ctx.fill();
  }

  drawCloudEffect(effect) {
    const curlX = Math.cos(this.time * effect.curlSpeed + effect.curlPhase) * 20;
    const curlY = Math.sin(this.time * effect.curlSpeed + effect.curlPhase) * 20;
    const pulse = Math.sin(this.time * effect.speed + effect.phase) * 0.5 + 0.5;

    const x = effect.baseX + curlX;
    const y = effect.baseY + curlY;
    const alpha = effect.alpha * pulse;

    this.ctx.save();
    this.ctx.translate(x, y);

    for (let i = 0; i < 3; i++) {
      const offsetAngle = (Math.PI * 2 / 3) * i + this.time * 0.001;
      const offsetX = Math.cos(offsetAngle) * effect.size * 0.3;
      const offsetY = Math.sin(offsetAngle) * effect.size * 0.3;

      const cloudSize = effect.size * (0.8 + i * 0.1);
      const gradient = this.ctx.createRadialGradient(offsetX, offsetY, 0, offsetX, offsetY, cloudSize);
      gradient.addColorStop(0, this.hexToRgba(this.colors[2], alpha * 0.6));
      gradient.addColorStop(0.5, this.hexToRgba(this.colors[2], alpha * 0.3));
      gradient.addColorStop(1, this.hexToRgba(this.colors[2], 0));

      this.ctx.fillStyle = gradient;
      this.ctx.beginPath();
      this.ctx.arc(offsetX, offsetY, cloudSize, 0, Math.PI * 2);
      this.ctx.fill();
    }

    this.ctx.restore();

    const glowSize = effect.size * 1.8;
    const glowGradient = this.ctx.createRadialGradient(x, y, 0, x, y, glowSize);
    glowGradient.addColorStop(0, this.hexToRgba(this.colors[2], alpha * 0.25));
    glowGradient.addColorStop(1, this.hexToRgba(this.colors[2], 0));
    this.ctx.fillStyle = glowGradient;
    this.ctx.beginPath();
    this.ctx.arc(x, y, glowSize, 0, Math.PI * 2);
    this.ctx.fill();
  }

  drawStrands() {
    this.strands.forEach((strand, strandIndex) => {
      this.ctx.save();
      this.ctx.translate(this.centerX, this.centerY);
      this.ctx.rotate(Math.PI / 6);

      this.ctx.strokeStyle = this.hexToRgba(strand.color, 0.9);
      this.ctx.lineWidth = strand.width;
      this.ctx.lineCap = 'round';
      this.ctx.lineJoin = 'round';

      this.ctx.beginPath();

      strand.points.forEach((point, i) => {
        const rotation = this.time * 0.001 + point.phase;
        const x = Math.sin(rotation) * point.amplitude;
        const y = point.y;

        if (i === 0) {
          this.ctx.moveTo(x, y);
        } else {
          const prevPoint = strand.points[i - 1];
          const prevRotation = this.time * 0.001 + prevPoint.phase;
          const prevX = Math.sin(prevRotation) * prevPoint.amplitude;
          const prevY = prevPoint.y;

          const cpX = (prevX + x) / 2;
          const cpY = (prevY + y) / 2;

          this.ctx.quadraticCurveTo(cpX, cpY, x, y);
        }
      });

      this.ctx.stroke();

      strand.points.forEach((point, i) => {
        const rotation = this.time * 0.001 + point.phase;
        const x = Math.sin(rotation) * point.amplitude;
        const y = point.y;

        const glowSize = 12;
        const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, glowSize);
        gradient.addColorStop(0, this.hexToRgba(strand.glowColor, 0.4));
        gradient.addColorStop(1, this.hexToRgba(strand.glowColor, 0));
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(x, y, glowSize, 0, Math.PI * 2);
        this.ctx.fill();

        const shadowSize = 15;
        const shadowGradient = this.ctx.createRadialGradient(x, y, 0, x, y, shadowSize);
        shadowGradient.addColorStop(0, this.hexToRgba(strand.shadowColor, 0.15));
        shadowGradient.addColorStop(1, this.hexToRgba(strand.shadowColor, 0));
        this.ctx.fillStyle = shadowGradient;
        this.ctx.beginPath();
        this.ctx.arc(x, y, shadowSize, 0, Math.PI * 2);
        this.ctx.fill();
      });

      this.ctx.restore();
    });
  }

  drawBasePairs() {
    this.basePairs.forEach(pair => {
      const rotation = this.time * 0.001 + pair.phase;
      const amplitude = 50;

      const x1 = Math.sin(rotation) * amplitude;
      const x2 = Math.sin(rotation + Math.PI) * amplitude;
      const y = pair.y;

      this.ctx.save();
      this.ctx.translate(this.centerX, this.centerY);
      this.ctx.rotate(Math.PI / 6);

      this.ctx.strokeStyle = this.hexToRgba(pair.color, 0.6);
      this.ctx.lineWidth = pair.width;
      this.ctx.lineCap = 'round';

      this.ctx.beginPath();
      this.ctx.moveTo(x1, y);
      this.ctx.lineTo(x2, y);
      this.ctx.stroke();

      this.ctx.fillStyle = this.hexToRgba(pair.color, 0.5);
      this.ctx.beginPath();
      this.ctx.arc(x1, y, pair.width * 0.8, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.beginPath();
      this.ctx.arc(x2, y, pair.width * 0.8, 0, Math.PI * 2);
      this.ctx.fill();

      this.ctx.restore();
    });
  }

  hexToRgba(hex, alpha) {
    const rgb = ColorEngine.hexToRgb(hex);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    this.drawGrid();
    this.drawDataStreams();
    this.drawBasePairs();
    this.drawStrands();
    this.drawThemeEffects();

    if (this.isPlaying) {
      this.time += 16;
    }
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;

    const animate = () => {
      if (!this.isRunning) return;
      this.render();
      this.animationId = requestAnimationFrame(animate);
    };

    animate();
  }

  stop() {
    this.isRunning = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  destroy() {
    this.stop();
    this.strands = [];
    this.basePairs = [];
    this.gridCells = [];
    this.dataStreams = [];
    this.themeEffects = [];
  }
}

/**
 * 注册页面 Step 4 - 烟花动画
 * 设计理念：多层烟花爆炸，庆祝注册成功
 * 特点：中心烟花、外围烟花、粒子拖尾
 */
export class PreciseCheckmarkAnimation {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = canvas.width;
    this.height = canvas.height;

    this.size = options.size || 280;
    this.centerX = this.width / 2;
    this.centerY = this.height / 2;

    this.themeName = options.themeName || 'theme-china-red';
    this.colors = ColorEngine.getAnimationColorsByTheme(this.themeName);

    this.time = 0;
    this.fireworks = [];
    this.particles = [];
    this.isRunning = false;
    this.animationId = null;
    this.isPlaying = false;

    this.initFireworks();
  }

  initFireworks() {
    this.fireworks = [];
    const fireworkCount = 5;

    for (let i = 0; i < fireworkCount; i++) {
      const angle = (Math.PI * 2 / fireworkCount) * i;
      const distance = 40 + Math.random() * 60;
      const delay = i * 300;

      this.fireworks.push({
        x: this.centerX + Math.cos(angle) * distance,
        y: this.centerY + Math.sin(angle) * distance,
        targetX: this.centerX + Math.cos(angle) * distance,
        targetY: this.centerY + Math.sin(angle) * distance,
        delay: delay,
        hasExploded: false,
        color: this.colors[Math.floor(Math.random() * this.colors.length)],
        particleCount: 40 + Math.floor(Math.random() * 30),
        explosionRadius: 60 + Math.random() * 40
      });
    }

    const centerFirework = {
      x: this.centerX,
      y: this.centerY,
      targetX: this.centerX,
      targetY: this.centerY,
      delay: 0,
      hasExploded: false,
      color: this.colors[0],
      particleCount: 80 + Math.floor(Math.random() * 40),
      explosionRadius: 80 + Math.random() * 40
    };

    this.fireworks.unshift(centerFirework);
  }

  setTheme(themeName) {
    this.themeName = themeName;
    this.colors = ColorEngine.getAnimationColorsByTheme(this.themeName);
  }

  resize(width, height) {
    this.width = width;
    this.height = height;
    this.centerX = width / 2;
    this.centerY = height / 2;
    this.canvas.width = width;
    this.canvas.height = height;
    this.initFireworks();
  }

  play() {
    this.isPlaying = true;
    this.time = 0;
    this.initFireworks();
  }

  reset() {
    this.isPlaying = false;
    this.time = 0;
    this.initFireworks();
  }

  explodeFirework(firework) {
    const particles = [];

    for (let i = 0; i < firework.particleCount; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 2 + Math.random() * 4;
      const distance = Math.random() * firework.explosionRadius;

      particles.push({
        x: firework.x,
        y: firework.y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 1,
        size: 2 + Math.random() * 3,
        alpha: 0.8 + Math.random() * 0.2,
        color: firework.color,
        decay: 0.008 + Math.random() * 0.008,
        trail: [],
        trailLength: 8 + Math.floor(Math.random() * 6),
        gravity: 0.05 + Math.random() * 0.03
      });
    }

    this.particles.push(...particles);
  }

  updateFireworks() {
    this.fireworks.forEach(firework => {
      if (!firework.hasExploded && this.time >= firework.delay) {
        firework.hasExploded = true;
        this.explodeFirework(firework);
      }
    });
  }

  updateParticles() {
    this.particles = this.particles.filter(particle => {
      particle.x += particle.vx;
      particle.y += particle.vy;
      particle.vy += particle.gravity;
      particle.alpha -= particle.decay;

      particle.trail.unshift({ x: particle.x, y: particle.y, alpha: particle.alpha });
      if (particle.trail.length > particle.trailLength) {
        particle.trail.pop();
      }

      return particle.alpha > 0;
    });
  }

  drawFireworks() {
    this.fireworks.forEach(firework => {
      if (!firework.hasExploded && this.time >= firework.delay) {
        const progress = Math.min((this.time - firework.delay) / 500, 1);
        const currentY = firework.y - progress * 50;

        this.ctx.fillStyle = this.hexToRgba(firework.color, 1 - progress);
        this.ctx.beginPath();
        this.ctx.arc(firework.x, currentY, 4, 0, Math.PI * 2);
        this.ctx.fill();

        const glowSize = 12;
        const gradient = this.ctx.createRadialGradient(firework.x, currentY, 0, firework.x, currentY, glowSize);
        gradient.addColorStop(0, this.hexToRgba(firework.color, 0.6));
        gradient.addColorStop(1, this.hexToRgba(firework.color, 0));
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(firework.x, currentY, glowSize, 0, Math.PI * 2);
        this.ctx.fill();
      }
    });
  }

  drawParticles() {
    this.particles.forEach(particle => {
      for (let i = particle.trail.length - 1; i >= 0; i--) {
        const trailPoint = particle.trail[i];
        const trailAlpha = trailPoint.alpha * (1 - i / particle.trail.length) * 0.5;
        const trailSize = particle.size * (1 - i / particle.trail.length * 0.3);

        this.ctx.fillStyle = this.hexToRgba(particle.color, trailAlpha);
        this.ctx.beginPath();
        this.ctx.arc(trailPoint.x, trailPoint.y, trailSize, 0, Math.PI * 2);
        this.ctx.fill();
      }

      this.ctx.fillStyle = this.hexToRgba(particle.color, particle.alpha);
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      this.ctx.fill();

      const glowSize = particle.size * 2.5;
      const gradient = this.ctx.createRadialGradient(particle.x, particle.y, 0, particle.x, particle.y, glowSize);
      gradient.addColorStop(0, this.hexToRgba(particle.color, particle.alpha * 0.5));
      gradient.addColorStop(1, this.hexToRgba(particle.color, 0));
      this.ctx.fillStyle = gradient;
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, glowSize, 0, Math.PI * 2);
      this.ctx.fill();
    });
  }

  hexToRgba(hex, alpha) {
    const rgb = ColorEngine.hexToRgb(hex);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    if (this.isPlaying) {
      this.updateFireworks();
      this.updateParticles();
      this.drawFireworks();
      this.drawParticles();
      this.time += 16;
    } else {
      this.drawParticles();
    }
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;

    const animate = () => {
      if (!this.isRunning) return;
      this.render();
      this.animationId = requestAnimationFrame(animate);
    };

    animate();
  }

  stop() {
    this.isRunning = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  destroy() {
    this.stop();
    this.fireworks = [];
    this.particles = [];
  }
}
