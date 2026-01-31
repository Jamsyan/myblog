/**
 * 3D 动画工具模块 - 创建平面但有厚度感的动画
 */

import { gsap } from 'gsap';

/**
 * 创建登录页面简单锁动画（平面+轻微3D厚度）
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function createSimpleLockAnimation(container, options = {}) {
  const {
    size = 100,
    primaryColor = 'var(--primary-color)',
    secondaryColor = 'var(--secondary-color)',
    accentColor = '#4A90E2'
  } = options;

  const lockContainer = document.createElement('div');
  lockContainer.className = 'simple-lock-container';
  lockContainer.style.cssText = `
    width: ${size}px;
    height: ${size}px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  const lockBody = document.createElement('div');
  lockBody.className = 'simple-lock-body';
  lockBody.style.cssText = `
    width: ${size * 0.6}px;
    height: ${size * 0.5}px;
    background: linear-gradient(135deg, ${primaryColor}, ${secondaryColor});
    border-radius: 8px;
    position: relative;
    box-shadow: 
      0 4px 12px rgba(0, 0, 0, 0.15),
      inset 0 2px 4px rgba(255, 255, 255, 0.3),
      0 0 0 1px rgba(255, 255, 255, 0.2);
  `;

  const lockShackle = document.createElement('div');
  lockShackle.className = 'simple-lock-shackle';
  lockShackle.style.cssText = `
    position: absolute;
    top: -${size * 0.15}px;
    left: 50%;
    transform: translateX(-50%);
    width: ${size * 0.35}px;
    height: ${size * 0.25}px;
    border: ${size * 0.08}px solid ${primaryColor};
    border-bottom: none;
    border-radius: ${size * 0.2}px ${size * 0.2}px 0 0;
    background: linear-gradient(135deg, ${accentColor}, ${primaryColor});
    box-shadow: 
      0 2px 8px rgba(0, 0, 0, 0.1),
      inset 0 1px 2px rgba(255, 255, 255, 0.2);
  `;

  const lockHole = document.createElement('div');
  lockHole.className = 'simple-lock-hole';
  lockHole.style.cssText = `
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: ${size * 0.2}px;
    height: ${size * 0.2}px;
    background: radial-gradient(circle, ${accentColor}, ${primaryColor});
    border-radius: 50%;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
  `;

  lockBody.appendChild(lockHole);
  lockContainer.appendChild(lockShackle);
  lockContainer.appendChild(lockBody);
  container.appendChild(lockContainer);

  const timeline = gsap.timeline({ repeat: -1, yoyo: true });

  timeline.to(lockContainer, {
    y: -8,
    duration: 1.5,
    ease: 'power1.inOut'
  });

  return {
    element: lockContainer,
    timeline,
    destroy: () => {
      timeline.kill();
      lockContainer.remove();
    }
  };
}

/**
 * 创建3D球体动画（播放一次）
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function create3DSphereOneShot(container, options = {}) {
  const {
    size = 80,
    colors = ['#4A90E2', '#7B68EE', '#00CED1', '#FFFFFF'],
    duration = 2
  } = options;

  const sphere = document.createElement('div');
  sphere.className = 'glass-3d-sphere';
  sphere.style.cssText = `
    width: ${size}px;
    height: ${size}px;
    background: linear-gradient(135deg, ${colors[0]}, ${colors[1]});
    border-radius: 50%;
    position: relative;
    transform-style: preserve-3d;
    perspective: 600px;
    box-shadow: 
      0 20px 60px rgba(0, 0, 0, 0.3),
      inset 0 -10px 20px rgba(255, 255, 255, 0.3),
      inset 0 10px 20px rgba(0, 0, 0, 0.1);
  `;

  const innerSphere = document.createElement('div');
  innerSphere.className = 'glass-3d-sphere-inner';
  innerSphere.style.cssText = `
    position: absolute;
    top: 15%;
    left: 15%;
    width: 30%;
    height: 30%;
    background: radial-gradient(circle, ${colors[3]}, transparent);
    border-radius: 50%;
    filter: blur(2px);
  `;

  sphere.appendChild(innerSphere);
  container.appendChild(sphere);

  const timeline = gsap.timeline();

  timeline.from(sphere, {
    scale: 0,
    opacity: 0,
    duration: 0.6,
    ease: 'back.out(1.7)'
  });

  timeline.to(sphere, {
    rotationX: 180,
    rotationY: 180,
    duration: duration,
    ease: 'power2.out'
  });

  timeline.to(sphere, {
    scale: 1.1,
    duration: 0.4,
    ease: 'power1.inOut'
  }, '-=0.2');

  timeline.to(sphere, {
    scale: 1,
    duration: 0.4,
    ease: 'power1.inOut'
  });

  return {
    element: sphere,
    timeline,
    destroy: () => {
      timeline.kill();
      sphere.remove();
    }
  };
}

/**
 * 创建3D立方体动画（播放一次）
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function create3DCubeOneShot(container, options = {}) {
  const {
    size = 80,
    colors = ['#4A90E2', '#7B68EE', '#00CED1', '#FFFFFF'],
    duration = 2.5
  } = options;

  const cube = document.createElement('div');
  cube.className = 'glass-3d-cube';
  cube.style.cssText = `
    width: ${size}px;
    height: ${size}px;
    position: relative;
    transform-style: preserve-3d;
    perspective: 600px;
  `;

  const faces = [
    { transform: `translateZ(${size / 2}px)`, color: colors[0] },
    { transform: `rotateY(180deg) translateZ(${size / 2}px)`, color: colors[1] },
    { transform: `rotateY(-90deg) translateZ(${size / 2}px)`, color: colors[2] },
    { transform: `rotateY(90deg) translateZ(${size / 2}px)`, color: colors[3] },
    { transform: `rotateX(-90deg) translateZ(${size / 2}px)`, color: colors[0] },
    { transform: `rotateX(90deg) translateZ(${size / 2}px)`, color: colors[1] }
  ];

  faces.forEach((face, index) => {
    const faceElement = document.createElement('div');
    faceElement.className = 'glass-3d-cube-face';
    faceElement.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      background: linear-gradient(135deg, ${face.color}, ${colors[(index + 1) % colors.length]});
      opacity: 0.8;
      border: 1px solid rgba(255, 255, 255, 0.4);
      backdrop-filter: blur(10px);
      transform: ${face.transform};
      box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.2);
    `;
    cube.appendChild(faceElement);
  });

  container.appendChild(cube);

  const timeline = gsap.timeline();

  timeline.from(cube, {
    scale: 0,
    opacity: 0,
    duration: 0.6,
    ease: 'back.out(1.7)'
  });

  timeline.to(cube, {
    rotationX: 360,
    rotationY: 360,
    duration: duration,
    ease: 'power2.out'
  });

  timeline.to(cube, {
    scale: 1.1,
    duration: 0.4,
    ease: 'power1.inOut'
  }, '-=0.3');

  timeline.to(cube, {
    scale: 1,
    duration: 0.4,
    ease: 'power1.inOut'
  });

  return {
    element: cube,
    timeline,
    destroy: () => {
      timeline.kill();
      cube.remove();
    }
  };
}

/**
 * 创建3D圆环动画（播放一次）
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function create3DRingOneShot(container, options = {}) {
  const {
    size = 100,
    thickness = 15,
    colors = ['#4A90E2', '#7B68EE', '#00CED1', '#FFFFFF'],
    duration = 2.5
  } = options;

  const ring = document.createElement('div');
  ring.className = 'glass-3d-ring';
  ring.style.cssText = `
    width: ${size}px;
    height: ${size}px;
    position: relative;
    transform-style: preserve-3d;
    perspective: 600px;
  `;

  const outerRing = document.createElement('div');
  outerRing.className = 'glass-3d-ring-outer';
  outerRing.style.cssText = `
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: ${thickness}px solid;
    border-color: ${colors[0]};
    border-color: ${colors[0]} transparent ${colors[1]} transparent;
    opacity: 0.85;
    box-shadow: 
      0 0 30px ${colors[0]},
      inset 0 0 20px rgba(255, 255, 255, 0.3);
  `;

  const innerRing = document.createElement('div');
  innerRing.className = 'glass-3d-ring-inner';
  innerRing.style.cssText = `
    position: absolute;
    top: 20%;
    left: 20%;
    width: 60%;
    height: 60%;
    border-radius: 50%;
    border: ${thickness / 2}px solid;
    border-color: ${colors[2]};
    border-color: ${colors[2]} transparent ${colors[3]} transparent;
    opacity: 0.7;
    box-shadow: 0 0 20px ${colors[2]};
  `;

  ring.appendChild(outerRing);
  ring.appendChild(innerRing);
  container.appendChild(ring);

  const timeline = gsap.timeline();

  timeline.from(ring, {
    scale: 0,
    opacity: 0,
    duration: 0.6,
    ease: 'back.out(1.7)'
  });

  timeline.to(outerRing, {
    rotation: 360,
    duration: duration,
    ease: 'power2.out'
  });

  timeline.to(innerRing, {
    rotation: -360,
    duration: duration * 0.8,
    ease: 'power2.out'
  }, 0);

  timeline.to(ring, {
    scale: 1.1,
    duration: 0.4,
    ease: 'power1.inOut'
  }, '-=0.3');

  timeline.to(ring, {
    scale: 1,
    duration: 0.4,
    ease: 'power1.inOut'
  });

  return {
    element: ring,
    timeline,
    destroy: () => {
      timeline.kill();
      ring.remove();
    }
  };
}

/**
 * 创建圆形到对勾的形变动画（不旋转）
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function createCircleToCheckmarkNoRotate(container, options = {}) {
  const {
    size = 160,
    colors = ['#4CAF50', '#81C784', '#FFFFFF'],
    duration = 1.5
  } = options;

  const svgContainer = document.createElement('div');
  svgContainer.className = 'glass-checkmark-container';
  svgContainer.style.cssText = `
    width: ${size}px;
    height: ${size}px;
    position: relative;
  `;

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 100 100');
  svg.style.cssText = `
    width: 100%;
    height: 100%;
    overflow: visible;
  `;

  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
  gradient.setAttribute('id', 'checkmarkGradient');
  gradient.setAttribute('x1', '0%');
  gradient.setAttribute('y1', '0%');
  gradient.setAttribute('x2', '100%');
  gradient.setAttribute('y2', '100%');

  const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
  stop1.setAttribute('offset', '0%');
  stop1.setAttribute('style', `stop-color:${colors[0]};stop-opacity:1`);

  const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
  stop2.setAttribute('offset', '100%');
  stop2.setAttribute('style', `stop-color:${colors[1]};stop-opacity:1`);

  gradient.appendChild(stop1);
  gradient.appendChild(stop2);
  defs.appendChild(gradient);
  svg.appendChild(defs);

  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', '50');
  circle.setAttribute('cy', '50');
  circle.setAttribute('r', '40');
  circle.setAttribute('fill', 'none');
  circle.setAttribute('stroke', 'url(#checkmarkGradient)');
  circle.setAttribute('stroke-width', '4');
  circle.style.cssText = `
    stroke-dasharray: 251.2;
    stroke-dashoffset: 251.2;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
  `;

  const checkmark = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  checkmark.setAttribute('d', 'M30 50 L45 65 L70 35');
  checkmark.setAttribute('fill', 'none');
  checkmark.setAttribute('stroke', colors[2]);
  checkmark.setAttribute('stroke-width', '4');
  checkmark.setAttribute('stroke-linecap', 'round');
  checkmark.setAttribute('stroke-linejoin', 'round');
  checkmark.style.cssText = `
    stroke-dasharray: 56.6;
    stroke-dashoffset: 56.6;
    opacity: 0;
  `;

  svg.appendChild(circle);
  svg.appendChild(checkmark);
  svgContainer.appendChild(svg);

  container.appendChild(svgContainer);

  const timeline = gsap.timeline();

  timeline.from(svgContainer, {
    scale: 0,
    opacity: 0,
    duration: 0.4,
    ease: 'back.out(1.7)'
  });

  timeline.to(circle, {
    strokeDashoffset: 0,
    duration: duration * 0.6,
    ease: 'power2.out'
  });

  timeline.to(circle, {
    scale: 1.05,
    duration: 0.2,
    ease: 'power1.inOut'
  });

  timeline.to(circle, {
    scale: 1,
    duration: 0.2,
    ease: 'power1.inOut'
  });

  timeline.to(checkmark, {
    strokeDashoffset: 0,
    opacity: 1,
    duration: duration * 0.5,
    ease: 'power2.out'
  }, '-=0.3');

  return {
    element: svgContainer,
    timeline,
    destroy: () => {
      timeline.kill();
      svgContainer.remove();
    }
  };
}

/**
 * 清理所有动画
 * @param {Array} animations - 动画对象数组
 */
export function cleanupAnimations(animations) {
  animations.forEach(animation => {
    if (animation && animation.destroy) {
      animation.destroy();
    }
  });
}