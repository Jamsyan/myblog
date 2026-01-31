/**
 * Three.js 场景管理器 - 管理 3D 场景、相机、渲染器
 */

import * as THREE from 'three';

/**
 * 3D 场景管理器类
 */
export class ThreeScene {
  constructor(container, options = {}) {
    const {
      width = container.clientWidth,
      height = container.clientHeight,
      backgroundColor = null,
      antialias = true
    } = options;

    this.container = container;
    this.width = width;
    this.height = height;

    this.scene = new THREE.Scene();
    if (backgroundColor !== null) {
      this.scene.background = new THREE.Color(backgroundColor);
    }

    this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    this.camera.position.z = 5;

    this.renderer = new THREE.WebGLRenderer({ antialias, alpha: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.domElement.style.position = 'absolute';
    this.renderer.domElement.style.top = '0';
    this.renderer.domElement.style.left = '0';
    this.renderer.domElement.style.width = '100%';
    this.renderer.domElement.style.height = '100%';
    this.renderer.domElement.style.pointerEvents = 'none';

    container.appendChild(this.renderer.domElement);

    this.objects = [];
    this.lights = [];
    this.animationId = null;

    this.setupLights();
    this.setupResizeHandler();
    this.startRenderLoop();
  }

  setupLights() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    this.scene.add(ambientLight);
    this.lights.push(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.9);
    directionalLight.position.set(5, 5, 5);
    this.scene.add(directionalLight);
    this.lights.push(directionalLight);

    const pointLight = new THREE.PointLight(0xffffff, 0.6);
    pointLight.position.set(-5, 5, 5);
    this.scene.add(pointLight);
    this.lights.push(pointLight);
  }

  setupResizeHandler() {
    this.resizeHandler = () => {
      this.width = this.container.clientWidth;
      this.height = this.container.clientHeight;

      this.camera.aspect = this.width / this.height;
      this.camera.updateProjectionMatrix();

      this.renderer.setSize(this.width, this.height);
    };

    window.addEventListener('resize', this.resizeHandler);
  }

  startRenderLoop() {
    const animate = () => {
      try {
        this.renderer.render(this.scene, this.camera);
        this.animationId = requestAnimationFrame(animate);
      } catch (error) {
        console.error('[ThreeScene] 渲染错误:', error);
      }
    };

    this.animationId = requestAnimationFrame(animate);
  }

  stopRenderLoop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  addObject(object) {
    this.objects.push(object);
    this.scene.add(object);
  }

  removeObject(object) {
    const index = this.objects.indexOf(object);
    if (index > -1) {
      this.objects.splice(index, 1);
      this.scene.remove(object);
      if (object.geometry) {
        object.geometry.dispose();
      }
      if (object.material) {
        if (Array.isArray(object.material)) {
          object.material.forEach(material => material.dispose());
        } else {
          object.material.dispose();
        }
      }
    }
  }

  clearObjects() {
    this.objects.forEach(object => {
      this.scene.remove(object);
      if (object.geometry) {
        object.geometry.dispose();
      }
      if (object.material) {
        if (Array.isArray(object.material)) {
          object.material.forEach(material => material.dispose());
        } else {
          object.material.dispose();
        }
      }
    });
    this.objects = [];
  }

  setBackgroundColor(color) {
    this.scene.background = new THREE.Color(color);
  }

  resize() {
    this.width = this.container.clientWidth;
    this.height = this.container.clientHeight;

    this.camera.aspect = this.width / this.height;
    this.camera.updateProjectionMatrix();

    this.renderer.setSize(this.width, this.height);
  }

  render() {
    this.renderer.render(this.scene, this.camera);
  }

  dispose() {
    this.stopRenderLoop();
    window.removeEventListener('resize', this.resizeHandler);

    this.clearObjects();

    this.lights.forEach(light => {
      this.scene.remove(light);
    });

    if (this.renderer.domElement && this.renderer.domElement.parentNode) {
      this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
    }

    this.renderer.dispose();
  }
}

/**
 * 创建亚克力玻璃材质
 * @param {Object} options - 材质选项
 * @returns {THREE.Material} 玻璃材质
 */
export function createAcrylicMaterial(options = {}) {
  const {
    color = 0xffffff,
    opacity = 0.8,
    roughness = 0.05,
    metalness = 0.1,
    transparent = true
  } = options;

  return new THREE.MeshPhysicalMaterial({
    color,
    opacity,
    roughness,
    metalness,
    transparent,
    transmission: 0.95,
    thickness: 1.0,
    clearcoat: 1.0,
    clearcoatRoughness: 0.05,
    side: THREE.DoubleSide
  });
}

/**
 * 创建渐变材质
 * @param {Array} colors - 颜色数组
 * @param {Object} options - 材质选项
 * @returns {THREE.Material} 渐变材质
 */
export function createGradientMaterial(colors, options = {}) {
  const {
    opacity = 0.9,
    roughness = 0.1,
    metalness = 0.2
  } = options;

  const color = new THREE.Color(colors[0]);
  const emissive = new THREE.Color(colors[1] || colors[0]);

  return new THREE.MeshPhysicalMaterial({
    color,
    emissive,
    emissiveIntensity: 0.3,
    opacity,
    roughness,
    metalness,
    transparent: true,
    side: THREE.DoubleSide
  });
}