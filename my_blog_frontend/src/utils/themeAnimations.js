/**
 * 主题专用动画效果库
 * 针对三种主题色设计哲学定制动画效果
 */

/**
 * 中国红主题 - 火焰粒子流效果（增强版）
 * 设计哲学：热闹的春节、天安门广场、唐人街
 * 动画特点：密集人群、灯笼光晕、烟花爆炸、祥云流动
 */
export class FlameParticleFlow {
  constructor(options = {}) {
    this.maxParticles = options.maxParticles || 200;
    this.speed = options.speed || 1.5;
    this.colors = options.colors || ['#B71C1C', '#C62828', '#E53935', '#FFA726', '#FFD700', '#FFFFFF'];
    this.particles = [];
    this.lanterns = [];
    this.fireworks = [];
    this.clouds = [];
    this.initParticles();
    this.initLanterns();
    this.initFireworks();
    this.initClouds();
  }

  initParticles() {
    this.particles = [];
    for (let i = 0; i < this.maxParticles; i++) {
      this.particles.push(this.createParticle());
    }
  }

  initLanterns() {
    this.lanterns = [];
    for (let i = 0; i < 6; i++) {
      this.lanterns.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight * 0.6 + 50,
        radius: 40 + Math.random() * 30,
        phase: Math.random() * Math.PI * 2,
        speed: 0.02 + Math.random() * 0.01,
        colorIndex: Math.floor(Math.random() * 3)
      });
    }
  }

  initFireworks() {
    this.fireworks = [];
    for (let i = 0; i < 3; i++) {
      this.fireworks.push(this.createFirework());
    }
  }

  createFirework() {
    return {
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight * 0.5 + 100,
      particles: [],
      phase: 0,
      maxPhase: 60,
      colorIndex: Math.floor(Math.random() * 3)
    };
  }

  initClouds() {
    this.clouds = [];
    for (let i = 0; i < 3; i++) {
      this.clouds.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight * 0.3 + 50,
        width: 200 + Math.random() * 200,
        height: 60 + Math.random() * 40,
        phase: Math.random() * Math.PI * 2,
        speed: 0.005 + Math.random() * 0.003,
        colorIndex: Math.floor(Math.random() * 2)
      });
    }
  }

  createParticle() {
    const colorIndex = this.colors.length > 0
      ? Math.floor(Math.random() * this.colors.length)
      : 0;

    return {
      x: Math.random() * window.innerWidth,
      y: window.innerHeight + Math.random() * 100,
      vx: (Math.random() - 0.5) * 0.8,
      vy: -(Math.random() * this.speed + 1.2),
      size: Math.random() * 6 + 2,
      life: Math.random() * 120 + 60,
      maxLife: 180,
      colorIndex: colorIndex,
      flickerIntensity: Math.random() * 0.4 + 0.6
    };
  }

  update(width, height, time) {
    this.particles.forEach((particle, index) => {
      particle.x += particle.vx + Math.sin(time * 0.002 + index) * 0.8;
      particle.y += particle.vy;
      particle.life--;

      const heightRatio = 1 - (particle.y / height);
      particle.colorIndex = Math.min(
        Math.max(0, Math.floor(heightRatio * this.colors.length)),
        this.colors.length - 1
      );

      particle.size = (2 + heightRatio * 4) * particle.flickerIntensity;

      if (particle.life <= 0 || particle.y < -50) {
        this.particles[index] = this.createParticle();
      }
    });

    this.lanterns.forEach(lantern => {
      lantern.phase += lantern.speed;
    });

    this.fireworks.forEach((firework, fwIndex) => {
      firework.phase++;

      if (firework.phase === 10) {
        for (let i = 0; i < 20; i++) {
          const angle = (Math.PI * 2 / 20) * i;
          const speed = 2 + Math.random() * 2;
          firework.particles.push({
            x: firework.x,
            y: firework.y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            size: 2 + Math.random() * 2,
            life: 60 + Math.random() * 30,
            maxLife: 90,
            colorIndex: Math.min(firework.colorIndex, this.colors.length - 1)
          });
        }
      }

      firework.particles.forEach((p, pIndex) => {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.05;
        p.life--;

        if (p.life <= 0) {
          firework.particles.splice(pIndex, 1);
        }
      });

      if (firework.phase >= firework.maxPhase) {
        this.fireworks[fwIndex] = this.createFirework();
      }
    });

    this.clouds.forEach(cloud => {
      cloud.phase += cloud.speed;
    });

    return { particles: this.particles, lanterns: this.lanterns, fireworks: this.fireworks, clouds: this.clouds };
  }

  render(ctx, data) {
    const { particles, lanterns, fireworks, clouds } = data;

    ctx.globalCompositeOperation = 'source-over';

    particles.forEach(particle => {
      const color = this.colors[particle.colorIndex];
      const alpha = (particle.life / particle.maxLife) * particle.flickerIntensity;

      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      ctx.fillStyle = this.hexToRgba(color, alpha);
      ctx.fill();

      if (particle.size > 3) {
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size * 1.5, 0, Math.PI * 2);
        ctx.fillStyle = this.hexToRgba(color, alpha * 0.3);
        ctx.fill();
      }
    });

    ctx.globalCompositeOperation = 'lighter';

    lanterns.forEach(lantern => {
      const baseColor = this.colors[lantern.colorIndex];
      const glowAlpha = 0.6 + Math.sin(lantern.phase) * 0.2;

      const gradient = ctx.createRadialGradient(
        lantern.x, lantern.y, 0,
        lantern.x, lantern.y, lantern.radius
      );
      gradient.addColorStop(0, this.hexToRgba(baseColor, glowAlpha));
      gradient.addColorStop(0.3, this.hexToRgba(baseColor, glowAlpha * 0.6));
      gradient.addColorStop(0.6, this.hexToRgba(baseColor, glowAlpha * 0.3));
      gradient.addColorStop(1, this.hexToRgba(baseColor, 0));

      ctx.beginPath();
      ctx.arc(lantern.x, lantern.y, lantern.radius, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.shadowColor = this.hexToRgba(baseColor, glowAlpha * 0.8);
      ctx.shadowBlur = 20;
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    fireworks.forEach(firework => {
      const baseColor = this.colors[firework.colorIndex];

      firework.particles.forEach(p => {
        const alpha = p.life / p.maxLife;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = this.hexToRgba(baseColor, alpha);
        ctx.fill();

        if (p.size > 2) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size * 1.5, 0, Math.PI * 2);
          ctx.fillStyle = this.hexToRgba(baseColor, alpha * 0.4);
          ctx.fill();
        }
      });
    });

    clouds.forEach(cloud => {
      const baseColor = this.colors[cloud.colorIndex];
      const cloudAlpha = 0.15 + Math.sin(cloud.phase) * 0.05;

      const gradient = ctx.createLinearGradient(
        cloud.x - cloud.width / 2, cloud.y,
        cloud.x + cloud.width / 2, cloud.y
      );
      gradient.addColorStop(0, this.hexToRgba(baseColor, 0));
      gradient.addColorStop(0.3, this.hexToRgba(baseColor, cloudAlpha * 0.4));
      gradient.addColorStop(0.5, this.hexToRgba(baseColor, cloudAlpha * 0.6));
      gradient.addColorStop(0.7, this.hexToRgba(baseColor, cloudAlpha * 0.4));
      gradient.addColorStop(1, this.hexToRgba(baseColor, 0));

      ctx.beginPath();
      ctx.ellipse(
        cloud.x, cloud.y,
        cloud.width / 2, cloud.height / 2,
        0, 0, Math.PI * 2
      );
      ctx.fillStyle = gradient;
      ctx.filter = 'blur(15px)';
      ctx.fill();
      ctx.filter = 'none';
    });

    ctx.globalCompositeOperation = 'source-over';
  }

  hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') {
      console.warn('Invalid hex color:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    hex = hex.replace(/^#/, '');

    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    if (hex.length !== 6) {
      console.warn('Invalid hex format:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  setColors(colors) {
    this.colors = colors;
  }
}

/**
 * 中国红主题 - 上升流动波效果
 * 设计哲学：欣欣向荣、上升流动
 * 动画特点：波浪层叠、向上涌动、透明度渐变
 */
export class RisingWaveFlow {
  constructor(options = {}) {
    this.maxWaves = options.maxWaves || 4;
    this.speed = options.speed || 0.8;
    this.colors = options.colors || ['#C62828', '#E53935', '#FFCDD2'];
    this.waves = [];
    this.initWaves();
  }

  initWaves() {
    this.waves = [];
    for (let i = 0; i < this.maxWaves; i++) {
      this.waves.push({
        amplitude: 30 + i * 20,
        frequency: 0.01 + i * 0.005,
        phase: i * Math.PI / 2,
        speed: this.speed + i * 0.2,
        yOffset: i * 50,
        colorIndex: this.colors.length > 0 ? i % this.colors.length : 0,
        alpha: 0.3 - i * 0.05
      });
    }
  }

  update(width, height, time) {
    this.waves.forEach(wave => {
      wave.phase += wave.speed * 0.02;
    });
    return this.waves;
  }

  render(ctx, waves, width, height) {
    waves.forEach((wave, index) => {
      const color = this.colors[wave.colorIndex];

      ctx.beginPath();
      ctx.moveTo(0, height);

      for (let x = 0; x <= width; x += 10) {
        const y = height - wave.yOffset -
          wave.amplitude * Math.sin(x * wave.frequency + wave.phase);
        ctx.lineTo(x, y);
      }

      ctx.lineTo(width, height);
      ctx.closePath();

      const gradient = ctx.createLinearGradient(0, height - wave.yOffset - wave.amplitude * 2, 0, height);
      gradient.addColorStop(0, this.hexToRgba(color, wave.alpha));
      gradient.addColorStop(1, this.hexToRgba(color, 0));

      ctx.fillStyle = gradient;
      ctx.fill();
    });
  }

  hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') {
      console.warn('Invalid hex color:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    hex = hex.replace(/^#/, '');

    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    if (hex.length !== 6) {
      console.warn('Invalid hex format:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  setColors(colors) {
    this.colors = colors;
  }
}

/**
 * 中国红主题 - 脉冲光晕效果
 * 设计哲学：生命力、心跳脉冲
 * 动画特点：周期性脉冲、多层光晕、视觉冲击力
 */
export class PulseGlow {
  constructor(options = {}) {
    this.maxPulses = options.maxPulses || 3;
    this.colors = options.colors || ['#C62828', '#E53935', '#FFA726'];
    this.pulses = [];
    this.initPulses();
  }

  initPulses() {
    this.pulses = [];
    for (let i = 0; i < this.maxPulses; i++) {
      this.pulses.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        radius: 20 + Math.random() * 30,
        maxRadius: 150 + Math.random() * 100,
        speed: 0.5 + Math.random() * 0.5,
        colorIndex: this.colors.length > 0 ? i % this.colors.length : 0,
        alpha: 0.6,
        phase: i * Math.PI / 2
      });
    }
  }

  update(width, height, time) {
    this.pulses.forEach((pulse, index) => {
      pulse.radius += pulse.speed;
      pulse.alpha = 0.6 * (1 - pulse.radius / pulse.maxRadius);
      pulse.phase += 0.05;

      if (pulse.radius >= pulse.maxRadius) {
        this.pulses[index] = {
          x: Math.random() * width,
          y: Math.random() * height,
          radius: 20 + Math.random() * 30,
          maxRadius: 150 + Math.random() * 100,
          speed: 0.5 + Math.random() * 0.5,
          colorIndex: this.colors.length > 0 ? index % this.colors.length : 0,
          alpha: 0.6,
          phase: 0
        };
      }
    });
    return this.pulses;
  }

  render(ctx, pulses) {
    pulses.forEach(pulse => {
      const color = this.colors[pulse.colorIndex];

      for (let i = 3; i >= 0; i--) {
        const radius = Math.max(0, pulse.radius - i * 20);
        ctx.beginPath();
        ctx.arc(pulse.x, pulse.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = this.hexToRgba(color, pulse.alpha * (0.3 - i * 0.05));
        ctx.fill();
      }
    });
  }

  hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') {
      console.warn('Invalid hex color:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    hex = hex.replace(/^#/, '');

    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    if (hex.length !== 6) {
      console.warn('Invalid hex format:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  setColors(colors) {
    this.colors = colors;
  }
}

/**
 * 粉霞紫主题 - 丝绸流动效果（增强版）
 * 设计哲学：私密的诱惑、紫色旗袍、抖音美女
 * 动画特点：丝绸柔美、雾气缭绕、霓虹光效、呼吸脉动
 */
export class SilkFlow {
  constructor(options = {}) {
    this.maxCurves = options.maxCurves || 10;
    this.speed = options.speed || 0.5;
    this.colors = options.colors || ['#4A148C', '#7B1FA2', '#9C27B0', '#F06292', '#FFFFFF'];
    this.curves = [];
    this.mists = [];
    this.initCurves();
    this.initMists();
  }

  initCurves() {
    this.curves = [];
    for (let i = 0; i < this.maxCurves; i++) {
      this.curves.push({
        startY: (window.innerHeight / this.maxCurves) * i,
        amplitude: 50 + Math.random() * 50,
        frequency: 0.005 + Math.random() * 0.005,
        phase: Math.random() * Math.PI * 2,
        speed: this.speed + Math.random() * 0.3,
        colorIndex: this.colors.length > 0 ? i % this.colors.length : 0,
        thickness: 2 + Math.random() * 2,
        alpha: 0.4 + Math.random() * 0.3
      });
    }
  }

  initMists() {
    this.mists = [];
    for (let i = 0; i < 15; i++) {
      this.mists.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        radius: 80 + Math.random() * 120,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.2,
        phase: Math.random() * Math.PI * 2,
        speed: 0.01 + Math.random() * 0.005,
        colorIndex: this.colors.length > 0 ? Math.floor(Math.random() * this.colors.length) : 0,
        alpha: 0.08 + Math.random() * 0.12
      });
    }
  }

  update(width, height, time) {
    this.curves.forEach(curve => {
      curve.phase += curve.speed * 0.01;
    });

    this.mists.forEach(mist => {
      mist.x += mist.vx + Math.sin(time * 0.001 + mist.phase) * 0.5;
      mist.y += mist.vy + Math.cos(time * 0.001 + mist.phase) * 0.3;
      mist.phase += mist.speed;

      if (mist.x < -mist.radius) mist.x = width + mist.radius;
      if (mist.x > width + mist.radius) mist.x = -mist.radius;
      if (mist.y < -mist.radius) mist.y = height + mist.radius;
      if (mist.y > height + mist.radius) mist.y = -mist.radius;
    });

    return { curves: this.curves, mists: this.mists };
  }

  render(ctx, data) {
    const { curves, mists } = data;

    ctx.globalCompositeOperation = 'source-over';

    curves.forEach(curve => {
      const color = this.colors[curve.colorIndex];

      ctx.beginPath();
      ctx.moveTo(0, curve.startY);

      for (let x = 0; x <= width; x += 20) {
        const y = curve.startY +
          curve.amplitude * Math.sin(x * curve.frequency + curve.phase) +
          curve.amplitude * 0.5 * Math.sin(x * curve.frequency * 2 + curve.phase * 1.5);
        ctx.lineTo(x, y);
      }

      ctx.strokeStyle = this.hexToRgba(color, curve.alpha);
      ctx.lineWidth = curve.thickness;
      ctx.lineCap = 'round';
      ctx.stroke();

      const gradient = ctx.createLinearGradient(0, curve.startY - curve.amplitude, 0, curve.startY + curve.amplitude);
      gradient.addColorStop(0, this.hexToRgba(color, 0));
      gradient.addColorStop(0.5, this.hexToRgba(color, curve.alpha * 0.3));
      gradient.addColorStop(1, this.hexToRgba(color, 0));

      ctx.beginPath();
      ctx.moveTo(0, curve.startY);

      for (let x = 0; x <= width; x += 20) {
        const y = curve.startY +
          curve.amplitude * Math.sin(x * curve.frequency + curve.phase) +
          curve.amplitude * 0.5 * Math.sin(x * curve.frequency * 2 + curve.phase * 1.5);
        ctx.lineTo(x, y);
      }

      ctx.lineTo(width, curve.startY + curve.amplitude);
      ctx.lineTo(0, curve.startY + curve.amplitude);
      ctx.closePath();

      ctx.fillStyle = gradient;
      ctx.fill();
    });

    ctx.globalCompositeOperation = 'soft-light';

    mists.forEach(mist => {
      const color = this.colors[mist.colorIndex];
      const mistAlpha = mist.alpha * (0.8 + Math.sin(mist.phase) * 0.2);

      const gradient = ctx.createRadialGradient(
        mist.x, mist.y, 0,
        mist.x, mist.y, mist.radius
      );
      gradient.addColorStop(0, this.hexToRgba(color, mistAlpha * 0.6));
      gradient.addColorStop(0.3, this.hexToRgba(color, mistAlpha * 0.4));
      gradient.addColorStop(0.6, this.hexToRgba(color, mistAlpha * 0.2));
      gradient.addColorStop(1, this.hexToRgba(color, 0));

      ctx.beginPath();
      ctx.arc(mist.x, mist.y, mist.radius, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.filter = 'blur(25px)';
      ctx.fill();
      ctx.filter = 'none';
    });

    ctx.globalCompositeOperation = 'source-over';
  }

  hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') {
      console.warn('Invalid hex color:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    hex = hex.replace(/^#/, '');

    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    if (hex.length !== 6) {
      console.warn('Invalid hex format:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  setColors(colors) {
    this.colors = colors;
  }
}

/**
 * 粉霞紫主题 - 呼吸脉动效果（增强版）
 * 设计哲学：呼吸、暧昧、诱惑
 * 动画特点：缩放脉动、霓虹光效、柔和节奏
 */
export class BreathingPulse {
  constructor(options = {}) {
    this.maxOrbs = options.maxOrbs || 10;
    this.colors = options.colors || ['#7B1FA2', '#9C27B0', '#F06292', '#F3E5F5', '#FFFFFF'];
    this.orbs = [];
    this.initOrbs();
  }

  initOrbs() {
    this.orbs = [];
    for (let i = 0; i < this.maxOrbs; i++) {
      this.orbs.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        baseRadius: 40 + Math.random() * 60,
        currentRadius: 40 + Math.random() * 60,
        phase: Math.random() * Math.PI * 2,
        speed: 0.02 + Math.random() * 0.02,
        colorIndex: this.colors.length > 0 ? i % this.colors.length : 0,
        alpha: 0.3 + Math.random() * 0.3,
        hasNeon: Math.random() > 0.5
      });
    }
  }

  update(width, height, time) {
    this.orbs.forEach(orb => {
      orb.phase += orb.speed;
      orb.currentRadius = orb.baseRadius + Math.sin(orb.phase) * 20;
      orb.alpha = 0.3 + Math.sin(orb.phase) * 0.2;
    });
    return this.orbs;
  }

  render(ctx, orbs) {
    ctx.globalCompositeOperation = 'source-over';

    orbs.forEach(orb => {
      const color = this.colors[orb.colorIndex];

      const gradient = ctx.createRadialGradient(
        orb.x, orb.y, 0,
        orb.x, orb.y, orb.currentRadius
      );
      gradient.addColorStop(0, this.hexToRgba(color, orb.alpha));
      gradient.addColorStop(0.5, this.hexToRgba(color, orb.alpha * 0.5));
      gradient.addColorStop(1, this.hexToRgba(color, 0));

      ctx.beginPath();
      ctx.arc(orb.x, orb.y, orb.currentRadius, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();

      if (orb.hasNeon) {
        ctx.beginPath();
        ctx.arc(orb.x, orb.y, orb.currentRadius, 0, Math.PI * 2);
        ctx.strokeStyle = this.hexToRgba(color, orb.alpha * 0.8);
        ctx.lineWidth = 3;
        ctx.shadowColor = this.hexToRgba(color, orb.alpha * 0.9);
        ctx.shadowBlur = 15;
        ctx.stroke();
        ctx.shadowBlur = 0;
      }
    });

    ctx.globalCompositeOperation = 'source-over';
  }

  hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') {
      console.warn('Invalid hex color:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    hex = hex.replace(/^#/, '');

    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    if (hex.length !== 6) {
      console.warn('Invalid hex format:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  setColors(colors) {
    this.colors = colors;
  }
}

/**
 * 粉霞紫主题 - 迷雾效果
 * 设计哲学：神秘、诱惑、朦胧
 * 动画特点：雾气流动、多层叠加、柔和透明
 */
export class MistEffect {
  constructor(options = {}) {
    this.maxMists = options.maxMists || 8;
    this.speed = options.speed || 0.3;
    this.colors = options.colors || ['#7B1FA2', '#9C27B0', '#BA68C8', '#F3E5F5'];
    this.mists = [];
    this.initMists();
  }

  initMists() {
    this.mists = [];
    for (let i = 0; i < this.maxMists; i++) {
      this.mists.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        width: 200 + Math.random() * 300,
        height: 100 + Math.random() * 150,
        vx: (Math.random() - 0.5) * this.speed,
        vy: (Math.random() - 0.5) * this.speed * 0.5,
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.01,
        colorIndex: this.colors.length > 0 ? i % this.colors.length : 0,
        alpha: 0.1 + Math.random() * 0.2
      });
    }
  }

  update(width, height, time) {
    this.mists.forEach((mist, index) => {
      mist.x += mist.vx + Math.sin(time * 0.001 + index) * 0.3;
      mist.y += mist.vy + Math.cos(time * 0.001 + index) * 0.2;
      mist.rotation += mist.rotationSpeed;

      if (mist.x < -mist.width) mist.x = width + mist.width;
      if (mist.x > width + mist.width) mist.x = -mist.width;
      if (mist.y < -mist.height) mist.y = height + mist.height;
      if (mist.y > height + mist.height) mist.y = -mist.height;
    });
    return this.mists;
  }

  render(ctx, mists) {
    mists.forEach(mist => {
      const color = this.colors[mist.colorIndex];

      ctx.save();
      ctx.translate(mist.x, mist.y);
      ctx.rotate(mist.rotation);

      const gradient = ctx.createRadialGradient(0, 0, 0, 0, mist.width / 2);
      gradient.addColorStop(0, this.hexToRgba(color, mist.alpha));
      gradient.addColorStop(0.5, this.hexToRgba(color, mist.alpha * 0.5));
      gradient.addColorStop(1, this.hexToRgba(color, 0));

      ctx.beginPath();
      ctx.ellipse(0, 0, mist.width / 2, mist.height / 2, 0, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();

      ctx.restore();
    });
  }

  hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') {
      console.warn('Invalid hex color:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    hex = hex.replace(/^#/, '');

    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    if (hex.length !== 6) {
      console.warn('Invalid hex format:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  setColors(colors) {
    this.colors = colors;
  }
}

/**
 * 丹青蓝主题 - 水墨扩散效果（增强版）
 * 设计哲学：国风水墨、留白美学、山水意境
 * 动画特点：墨汁晕染、竹叶飘动、云雾流动、留白处理
 */
export class InkDiffusion {
  constructor(options = {}) {
    this.maxInkSpots = options.maxInkSpots || 15;
    this.speed = options.speed || 0.5;
    this.colors = options.colors || ['#0A2463', '#0D47A1', '#42A5F5', '#00ACC1', '#FFFFFF'];
    this.inkSpots = [];
    this.bambooLeaves = [];
    this.clouds = [];
    this.initInkSpots();
    this.initBambooLeaves();
    this.initClouds();
  }

  initInkSpots() {
    this.inkSpots = [];
    for (let i = 0; i < this.maxInkSpots; i++) {
      this.inkSpots.push(this.createInkSpot());
    }
  }

  initBambooLeaves() {
    this.bambooLeaves = [];
    for (let i = 0; i < 20; i++) {
      this.bambooLeaves.push(this.createBambooLeaf());
    }
  }

  createBambooLeaf() {
    return {
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      length: 30 + Math.random() * 40,
      width: 8 + Math.random() * 12,
      angle: Math.random() * Math.PI * 2,
      rotationSpeed: (Math.random() - 0.5) * 0.02,
      vx: (Math.random() - 0.5) * 0.8,
      vy: (Math.random() - 0.5) * 0.5,
      colorIndex: this.colors.length > 0 ? Math.floor(Math.random() * this.colors.length) : 0,
      alpha: 0.4 + Math.random() * 0.4,
      phase: Math.random() * Math.PI * 2,
      hasVeins: Math.random() > 0.5
    };
  }

  initClouds() {
    this.clouds = [];
    for (let i = 0; i < 8; i++) {
      this.clouds.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        width: 300 + Math.random() * 400,
        height: 100 + Math.random() * 150,
        vx: (Math.random() - 0.3) * 0.4,
        vy: (Math.random() - 0.5) * 0.3,
        phase: Math.random() * Math.PI * 2,
        speed: 0.008 + Math.random() * 0.004,
        colorIndex: Math.floor(Math.random() * 3),
        alpha: 0.12 + Math.random() * 0.08
      });
    }
  }

  createInkSpot() {
    return {
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      radius: 10 + Math.random() * 20,
      maxRadius: 100 + Math.random() * 150,
      speed: 0.3 + Math.random() * 0.4,
      colorIndex: this.colors.length > 0 ? Math.floor(Math.random() * this.colors.length) : 0,
      alpha: 0.5 + Math.random() * 0.3,
      diffusion: 0.1 + Math.random() * 0.1
    };
  }

  update(width, height, time) {
    this.inkSpots.forEach((spot, index) => {
      spot.radius += spot.speed;
      spot.alpha = 0.5 * (1 - spot.radius / spot.maxRadius);
      spot.diffusion += 0.001;

      if (spot.radius >= spot.maxRadius) {
        this.inkSpots[index] = this.createInkSpot();
      }
    });

    this.bambooLeaves.forEach(leaf => {
      leaf.x += leaf.vx + Math.sin(time * 0.001 + leaf.phase) * 0.5;
      leaf.y += leaf.vy + Math.cos(time * 0.001 + leaf.phase) * 0.3;
      leaf.angle += leaf.rotationSpeed;
      leaf.phase += 0.01;

      if (leaf.x < -50) leaf.x = width + 50;
      if (leaf.x > width + 50) leaf.x = -50;
      if (leaf.y < -50) leaf.y = height + 50;
      if (leaf.y > height + 50) leaf.y = -50;
    });

    this.clouds.forEach(cloud => {
      cloud.x += cloud.vx + Math.sin(time * 0.0008 + cloud.phase) * 0.5;
      cloud.y += cloud.vy + Math.cos(time * 0.0008 + cloud.phase) * 0.3;
      cloud.phase += cloud.speed;

      if (cloud.x < -cloud.width) cloud.x = width + cloud.width;
      if (cloud.x > width + cloud.width) cloud.x = -cloud.width;
      if (cloud.y < -cloud.height) cloud.y = height + cloud.height;
      if (cloud.y > height + cloud.height) cloud.y = -cloud.height;
    });

    return { inkSpots: this.inkSpots, bamboLeaves: this.bambooLeaves, clouds: this.clouds };
  }

  render(ctx, data) {
    const { inkSpots, bamboLeaves, clouds } = data;

    ctx.globalCompositeOperation = 'multiply';

    inkSpots.forEach(spot => {
      const color = this.colors[spot.colorIndex];

      const gradient = ctx.createRadialGradient(
        spot.x, spot.y, 0,
        spot.x, spot.y, spot.radius
      );

      gradient.addColorStop(0, this.hexToRgba(color, spot.alpha));
      gradient.addColorStop(0.3, this.hexToRgba(color, spot.alpha * 0.6));
      gradient.addColorStop(0.6, this.hexToRgba(color, spot.alpha * 0.3));
      gradient.addColorStop(1, this.hexToRgba(color, 0));

      ctx.beginPath();
      ctx.arc(spot.x, spot.y, spot.radius, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.filter = `blur(${spot.diffusion * 15}px)`;
      ctx.fill();
      ctx.filter = 'none';
    });

    ctx.globalCompositeOperation = 'source-over';

    bamboLeaves.forEach(leaf => {
      const color = this.colors[leaf.colorIndex];

      ctx.save();
      ctx.translate(leaf.x, leaf.y);
      ctx.rotate(leaf.angle);

      ctx.beginPath();
      ctx.moveTo(-leaf.length / 2, 0);
      ctx.quadraticCurveTo(0, -leaf.width / 2, leaf.length / 2, 0);
      ctx.quadraticCurveTo(leaf.length / 2, leaf.width / 2, leaf.length / 2, 0);
      ctx.closePath();

      ctx.fillStyle = this.hexToRgba(color, leaf.alpha);
      ctx.fill();

      if (leaf.hasVeins) {
        ctx.beginPath();
        ctx.moveTo(-leaf.length / 2, 0);
        ctx.lineTo(leaf.length / 2, 0);
        ctx.strokeStyle = this.hexToRgba(color, leaf.alpha * 0.6);
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      ctx.restore();
    });

    ctx.globalCompositeOperation = 'screen';

    clouds.forEach(cloud => {
      const color = this.colors[cloud.colorIndex];
      const cloudAlpha = cloud.alpha * (0.6 + Math.sin(cloud.phase) * 0.2);

      const gradient = ctx.createLinearGradient(
        cloud.x - cloud.width / 2, cloud.y,
        cloud.x + cloud.width / 2, cloud.y
      );
      gradient.addColorStop(0, this.hexToRgba(color, 0));
      gradient.addColorStop(0.4, this.hexToRgba(color, cloudAlpha * 0.4));
      gradient.addColorStop(0.6, this.hexToRgba(color, cloudAlpha * 0.6));
      gradient.addColorStop(0.8, this.hexToRgba(color, cloudAlpha * 0.4));
      gradient.addColorStop(1, this.hexToRgba(color, 0));

      ctx.beginPath();
      ctx.ellipse(
        cloud.x, cloud.y,
        cloud.width / 2, cloud.height / 2,
        0, 0, Math.PI * 2
      );
      ctx.fillStyle = gradient;
      ctx.filter = 'blur(20px)';
      ctx.fill();
      ctx.filter = 'none';
    });

    ctx.globalCompositeOperation = 'source-over';
  }

  hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') {
      console.warn('Invalid hex color:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    hex = hex.replace(/^#/, '');

    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    if (hex.length !== 6) {
      console.warn('Invalid hex format:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  setColors(colors) {
    this.colors = colors;
  }
}

/**
 * 丹青蓝主题 - 竹叶飘动效果
 * 设计哲学：国风、竹子、飘逸
 * 动画特点：竹叶形状、随风飘动、水墨风格
 */
export class BambooLeaves {
  constructor(options = {}) {
    this.maxLeaves = options.maxLeaves || 12;
    this.speed = options.speed || 0.8;
    this.colors = options.colors || ['#0D47A1', '#42A5F5', '#90CAF9'];
    this.leaves = [];
    this.initLeaves();
  }

  initLeaves() {
    this.leaves = [];
    for (let i = 0; i < this.maxLeaves; i++) {
      this.leaves.push(this.createLeaf());
    }
  }

  createLeaf() {
    return {
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      length: 30 + Math.random() * 40,
      width: 8 + Math.random() * 12,
      angle: Math.random() * Math.PI * 2,
      rotationSpeed: (Math.random() - 0.5) * 0.02,
      vx: (Math.random() - 0.5) * this.speed,
      vy: (Math.random() - 0.5) * this.speed * 0.5,
      colorIndex: this.colors.length > 0 ? Math.floor(Math.random() * this.colors.length) : 0,
      alpha: 0.4 + Math.random() * 0.4,
      phase: Math.random() * Math.PI * 2
    };
  }

  update(width, height, time) {
    this.leaves.forEach((leaf, index) => {
      leaf.x += leaf.vx + Math.sin(time * 0.001 + leaf.phase) * 0.5;
      leaf.y += leaf.vy + Math.cos(time * 0.001 + leaf.phase) * 0.3;
      leaf.angle += leaf.rotationSpeed;
      leaf.phase += 0.01;

      if (leaf.x < -50) leaf.x = width + 50;
      if (leaf.x > width + 50) leaf.x = -50;
      if (leaf.y < -50) leaf.y = height + 50;
      if (leaf.y > height + 50) leaf.y = -50;
    });
    return this.leaves;
  }

  render(ctx, leaves) {
    leaves.forEach(leaf => {
      const color = this.colors[leaf.colorIndex];

      ctx.save();
      ctx.translate(leaf.x, leaf.y);
      ctx.rotate(leaf.angle);

      ctx.beginPath();
      ctx.moveTo(-leaf.length / 2, 0);
      ctx.quadraticCurveTo(0, -leaf.width / 2, leaf.length / 2, 0);
      ctx.quadraticCurveTo(0, leaf.width / 2, -leaf.length / 2, 0);
      ctx.closePath();

      ctx.fillStyle = this.hexToRgba(color, leaf.alpha);
      ctx.fill();

      ctx.strokeStyle = this.hexToRgba(color, leaf.alpha * 0.6);
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.restore();
    });
  }

  hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') {
      console.warn('Invalid hex color:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    hex = hex.replace(/^#/, '');

    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    if (hex.length !== 6) {
      console.warn('Invalid hex format:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  setColors(colors) {
    this.colors = colors;
  }
}

/**
 * 丹青蓝主题 - 云雾流动效果
 * 设计哲学：国风、云雾、留白
 * 动画特点：云雾流动、水墨风格、留白处理
 */
export class CloudMist {
  constructor(options = {}) {
    this.maxClouds = options.maxClouds || 6;
    this.speed = options.speed || 0.4;
    this.colors = options.colors || ['#0D47A1', '#42A5F5', '#90CAF9', '#E3F2FD'];
    this.clouds = [];
    this.initClouds();
  }

  initClouds() {
    this.clouds = [];
    for (let i = 0; i < this.maxClouds; i++) {
      this.clouds.push(this.createCloud());
    }
  }

  createCloud() {
    return {
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      width: 300 + Math.random() * 400,
      height: 100 + Math.random() * 150,
      vx: (Math.random() - 0.3) * this.speed,
      vy: (Math.random() - 0.5) * this.speed * 0.3,
      colorIndex: this.colors.length > 0 ? Math.floor(Math.random() * this.colors.length) : 0,
      alpha: 0.15 + Math.random() * 0.2,
      phase: Math.random() * Math.PI * 2
    };
  }

  update(width, height, time) {
    this.clouds.forEach((cloud, index) => {
      cloud.x += cloud.vx + Math.sin(time * 0.0008 + cloud.phase) * 0.5;
      cloud.y += cloud.vy + Math.cos(time * 0.0008 + cloud.phase) * 0.3;
      cloud.phase += 0.005;

      if (cloud.x < -cloud.width) cloud.x = width + cloud.width;
      if (cloud.x > width + cloud.width) cloud.x = -cloud.width;
      if (cloud.y < -cloud.height) cloud.y = height + cloud.height;
      if (cloud.y > height + cloud.height) cloud.y = -cloud.height;
    });
    return this.clouds;
  }

  render(ctx, clouds) {
    clouds.forEach(cloud => {
      const color = this.colors[cloud.colorIndex];

      ctx.save();
      ctx.translate(cloud.x, cloud.y);

      const gradient = ctx.createRadialGradient(0, 0, 0, 0, cloud.width / 2);
      gradient.addColorStop(0, this.hexToRgba(color, cloud.alpha));
      gradient.addColorStop(0.4, this.hexToRgba(color, cloud.alpha * 0.6));
      gradient.addColorStop(0.8, this.hexToRgba(color, cloud.alpha * 0.2));
      gradient.addColorStop(1, this.hexToRgba(color, 0));

      ctx.beginPath();
      ctx.ellipse(0, 0, cloud.width / 2, cloud.height / 2, 0, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();

      ctx.filter = 'blur(20px)';
      ctx.beginPath();
      ctx.ellipse(0, 0, cloud.width / 2.5, cloud.height / 2.5, 0, 0, Math.PI * 2);
      ctx.fillStyle = this.hexToRgba(color, cloud.alpha * 0.5);
      ctx.fill();
      ctx.filter = 'none';

      ctx.restore();
    });
  }

  hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') {
      console.warn('Invalid hex color:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    hex = hex.replace(/^#/, '');

    if (hex.length === 3) {
      hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    if (hex.length !== 6) {
      console.warn('Invalid hex format:', hex);
      return `rgba(0, 0, 0, ${alpha})`;
    }

    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  setColors(colors) {
    this.colors = colors;
  }
}
