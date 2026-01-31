/**
 * Three.js 3D 动画工具 - 创建 3D 模型动画
 */

import * as THREE from 'three';
import { gsap } from 'gsap';
import { ThreeScene } from './threeScene.js';
import {
  createLockModel,
  createSphereModel,
  createCubeModel,
  createRingModel,
  createCircleToCheckmarkModel
} from './threeModels.js';

/**
 * 创建登录页面锁动画
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function createLockAnimation(container, options = {}) {
  try {
    const scene = new ThreeScene(container);

    const lockModel = createLockModel(options);
    scene.addObject(lockModel);

    const timeline = gsap.timeline({ repeat: -1, yoyo: true });

    timeline.to(lockModel.position, {
      y: 0.3,
      duration: 1.5,
      ease: 'power1.inOut'
    });

    timeline.to(lockModel.rotation, {
      z: 0.05,
      duration: 1.5,
      ease: 'power1.inOut'
    }, 0);

    timeline.to(lockModel.rotation, {
      x: Math.PI * 0.05,
      duration: 2,
      ease: 'power1.inOut'
    }, 0);

    return {
      scene,
      model: lockModel,
      timeline,
      destroy: () => {
        timeline.kill();
        scene.dispose();
      }
    };
  } catch (error) {
    console.error('[ThreeAnimation] 创建登录页面锁动画失败:', error);
    throw error;
  }
}

/**
 * 创建3D球体动画（注册步骤1）
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function createSphereAnimation(container, options = {}) {
  try {
    const scene = new ThreeScene(container);

    const sphereModel = createSphereModel(options);
    scene.addObject(sphereModel);

    const timeline = gsap.timeline();

    timeline.from(sphereModel.scale, {
      x: 0,
      y: 0,
      z: 0,
      duration: 0.8,
      ease: 'back.out(1.7)'
    });

    timeline.to(sphereModel.rotation, {
      x: Math.PI * 2,
      y: Math.PI * 2,
      z: Math.PI * 2,
      duration: 2.5,
      ease: 'power2.out'
    });

    timeline.to(sphereModel.scale, {
      x: 1.15,
      y: 1.15,
      z: 1.15,
      duration: 0.5,
      ease: 'power1.inOut'
    }, '-=0.2');

    timeline.to(sphereModel.scale, {
      x: 1,
      y: 1,
      z: 1,
      duration: 0.5,
      ease: 'power1.inOut'
    });

    return {
      scene,
      model: sphereModel,
      timeline,
      destroy: () => {
        timeline.kill();
        scene.dispose();
      }
    };
  } catch (error) {
    console.error('[ThreeAnimation] 创建3D球体动画失败:', error);
    throw error;
  }
}

/**
 * 创建3D立方体动画（注册步骤2）
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function createCubeAnimation(container, options = {}) {
  try {
    const scene = new ThreeScene(container);

    const cubeModel = createCubeModel(options);
    scene.addObject(cubeModel);

    const timeline = gsap.timeline();

    timeline.from(cubeModel.scale, {
      x: 0,
      y: 0,
      z: 0,
      duration: 0.8,
      ease: 'back.out(1.7)'
    });

    timeline.to(cubeModel.rotation, {
      x: Math.PI * 2,
      y: Math.PI * 2,
      z: Math.PI * 2,
      duration: 3,
      ease: 'power2.out'
    });

    timeline.to(cubeModel.position, {
      y: 0.3,
      duration: 0.5,
      ease: 'power1.inOut'
    });

    timeline.to(cubeModel.position, {
      y: 0,
      duration: 0.5,
      ease: 'power1.inOut'
    });

    timeline.to(cubeModel.scale, {
      x: 1.1,
      y: 1.1,
      z: 1.1,
      duration: 0.4,
      ease: 'power1.inOut'
    });

    timeline.to(cubeModel.scale, {
      x: 1,
      y: 1,
      z: 1,
      duration: 0.4,
      ease: 'power1.inOut'
    });

    return {
      scene,
      model: cubeModel,
      timeline,
      destroy: () => {
        timeline.kill();
        scene.dispose();
      }
    };
  } catch (error) {
    console.error('[ThreeAnimation] 创建3D立方体动画失败:', error);
    throw error;
  }
}

/**
 * 创建3D圆环动画（注册步骤3）
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function createRingAnimation(container, options = {}) {
  try {
    const scene = new ThreeScene(container);

    const ringModel = createRingModel(options);
    scene.addObject(ringModel);

    const outerRing = ringModel.children[0];
    const innerRing = ringModel.children[1];

    const timeline = gsap.timeline();

    timeline.from(ringModel.scale, {
      x: 0,
      y: 0,
      z: 0,
      duration: 0.8,
      ease: 'back.out(1.7)'
    });

    timeline.to(outerRing.rotation, {
      x: Math.PI * 2,
      y: Math.PI * 2,
      z: 0,
      duration: 3,
      ease: 'power2.out'
    });

    timeline.to(innerRing.rotation, {
      x: -Math.PI * 2,
      y: -Math.PI * 2,
      z: 0,
      duration: 2.5,
      ease: 'power2.out'
    }, 0);

    timeline.to(ringModel.scale, {
      x: 1.1,
      y: 1.1,
      z: 1.1,
      duration: 0.4,
      ease: 'power1.inOut'
    });

    timeline.to(ringModel.scale, {
      x: 1,
      y: 1,
      z: 1,
      duration: 0.4,
      ease: 'power1.inOut'
    });

    return {
      scene,
      model: ringModel,
      timeline,
      destroy: () => {
        timeline.kill();
        scene.dispose();
      }
    };
  } catch (error) {
    console.error('[ThreeAnimation] 创建3D圆环动画失败:', error);
    throw error;
  }
}

/**
 * 创建圆形到对勾的形变动画（注册步骤4）
 * @param {HTMLElement} container - 容器元素
 * @param {Object} options - 配置选项
 * @returns {Object} 动画控制对象
 */
export function createCircleToCheckmarkAnimation(container, options = {}) {
  try {
    const scene = new ThreeScene(container);

    const checkmarkModel = createCircleToCheckmarkModel(options);
    scene.addObject(checkmarkModel);

    const circle = checkmarkModel.children[0];
    const checkmarkGroup = checkmarkModel.children[1];

    const timeline = gsap.timeline();

    timeline.from(checkmarkModel.scale, {
      x: 0,
      y: 0,
      z: 0,
      duration: 0.6,
      ease: 'back.out(1.7)'
    });

    timeline.to(circle.scale, {
      x: 1.1,
      y: 1.1,
      z: 1.1,
      duration: 0.4,
      ease: 'power1.inOut'
    });

    timeline.to(circle.scale, {
      x: 1,
      y: 1,
      z: 1,
      duration: 0.3,
      ease: 'power1.inOut'
    });

    timeline.to(checkmarkGroup.scale, {
      x: 0,
      y: 0,
      z: 0,
      duration: 0.5,
      ease: 'back.out(1.7)'
    });

    timeline.to(checkmarkGroup.scale, {
      x: 1.2,
      y: 1.2,
      z: 1.2,
      duration: 0.4,
      ease: 'elastic.out(1, 0.5)'
    });

    timeline.to(checkmarkGroup.scale, {
      x: 1,
      y: 1,
      z: 1,
      duration: 0.3,
      ease: 'power1.inOut'
    });

    return {
      scene,
      model: checkmarkModel,
      timeline,
      destroy: () => {
        timeline.kill();
        scene.dispose();
      }
    };
  } catch (error) {
    console.error('[ThreeAnimation] 创建圆形到对勾形变动画失败:', error);
    throw error;
  }
}

/**
 * 清理所有动画
 * @param {Array} animations - 动画对象数组
 */
export function cleanupThreeAnimations(animations) {
  animations.forEach(animation => {
    if (animation && animation.destroy) {
      animation.destroy();
    }
  });
}