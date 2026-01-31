/**
 * Three.js 3D 模型创建器 - 创建各种3D几何体模型
 */

import * as THREE from 'three';
import { createAcrylicMaterial, createGradientMaterial } from './threeScene.js';

/**
 * 创建3D锁模型（登录页面）
 * @param {Object} options - 配置选项
 * @returns {THREE.Mesh} 锁模型
 */
export function createLockModel(options = {}) {
  const {
    size = 1,
    primaryColor = '#C62828',
    secondaryColor = '#E53935',
    accentColor = '#4A90E2'
  } = options;

  const lockGroup = new THREE.Group();

  const bodyGeometry = new THREE.BoxGeometry(size * 0.6, size * 0.4, size * 0.3);
  const bodyMaterial = createAcrylicMaterial({
    color: primaryColor,
    opacity: 0.85
  });
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
  body.position.y = -size * 0.1;
  lockGroup.add(body);

  const shackleGeometry = new THREE.TorusGeometry(size * 0.15, size * 0.04, 16, 100);
  const shackleMaterial = createAcrylicMaterial({
    color: accentColor,
    opacity: 0.9
  });
  const shackle = new THREE.Mesh(shackleGeometry, shackleMaterial);
  shackle.position.y = size * 0.15;
  shackle.rotation.x = Math.PI / 2;
  lockGroup.add(shackle);

  const holeGeometry = new THREE.CylinderGeometry(size * 0.1, size * 0.1, 32);
  const holeMaterial = createAcrylicMaterial({
    color: accentColor,
    opacity: 0.7
  });
  const hole = new THREE.Mesh(holeGeometry, holeMaterial);
  hole.rotation.x = Math.PI / 2;
  hole.position.y = -size * 0.1;
  lockGroup.add(hole);

  lockGroup.scale.set(1.5, 1.5, 1.5);

  return lockGroup;
}

/**
 * 创建3D球体模型（注册步骤1）
 * @param {Object} options - 配置选项
 * @returns {THREE.Mesh} 球体模型
 */
export function createSphereModel(options = {}) {
  const {
    size = 1,
    colors = ['#4A90E2', '#7B68EE', '#00CED1', '#FFFFFF']
  } = options;

  const sphereGeometry = new THREE.SphereGeometry(size * 0.5, 32, 32);
  const sphereMaterial = createGradientMaterial(colors, {
    opacity: 0.85
  });
  const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);

  sphere.scale.set(1.2, 1.2, 1.2);

  return sphere;
}

/**
 * 创建3D立方体模型（注册步骤2）
 * @param {Object} options - 配置选项
 * @returns {THREE.Mesh} 立方体模型
 */
export function createCubeModel(options = {}) {
  const {
    size = 1,
    colors = ['#4A90E2', '#7B68EE', '#00CED1', '#FFFFFF']
  } = options;

  const cubeGeometry = new THREE.BoxGeometry(size * 0.6, size * 0.6, size * 0.6);
  const cubeMaterial = createGradientMaterial(colors, {
    opacity: 0.85
  });
  const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);

  cube.scale.set(1.2, 1.2, 1.2);

  return cube;
}

/**
 * 创建3D圆环模型（注册步骤3）
 * @param {Object} options - 配置选项
 * @returns {THREE.Mesh} 圆环模型
 */
export function createRingModel(options = {}) {
  const {
    size = 1,
    colors = ['#4A90E2', '#7B68EE', '#00CED1', '#FFFFFF']
  } = options;

  const ringGroup = new THREE.Group();

  const outerRingGeometry = new THREE.TorusGeometry(size * 0.4, size * 0.08, 16, 100);
  const outerRingMaterial = createGradientMaterial(colors, {
    opacity: 0.85
  });
  const outerRing = new THREE.Mesh(outerRingGeometry, outerRingMaterial);
  ringGroup.add(outerRing);

  const innerRingGeometry = new THREE.TorusGeometry(size * 0.25, size * 0.05, 16, 100);
  const innerRingMaterial = createGradientMaterial(colors.slice(1), {
    opacity: 0.8
  });
  const innerRing = new THREE.Mesh(innerRingGeometry, innerRingMaterial);
  innerRing.rotation.x = Math.PI / 2;
  ringGroup.add(innerRing);

  ringGroup.scale.set(1.2, 1.2, 1.2);

  return ringGroup;
}

/**
 * 创建圆形到对勾的形变模型（注册步骤4）
 * @param {Object} options - 配置选项
 * @returns {THREE.Group} 形变模型组
 */
export function createCircleToCheckmarkModel(options = {}) {
  const {
    size = 1,
    colors = ['#4CAF50', '#81C784', '#FFFFFF']
  } = options;

  const modelGroup = new THREE.Group();

  const circleGeometry = new THREE.TorusGeometry(size * 0.4, size * 0.06, 32, 100);
  const circleMaterial = createGradientMaterial(colors, {
    opacity: 0.85
  });
  const circle = new THREE.Mesh(circleGeometry, circleMaterial);
  circle.rotation.x = Math.PI / 2;
  modelGroup.add(circle);

  const checkmarkGroup = new THREE.Group();
  const checkmarkMaterial = createAcrylicMaterial({
    color: colors[2],
    opacity: 0.95
  });

  const line1Geometry = new THREE.BoxGeometry(size * 0.3, size * 0.04, size * 0.04);
  const line1 = new THREE.Mesh(line1Geometry, checkmarkMaterial);
  line1.position.set(-size * 0.1, size * 0.05, 0);
  line1.rotation.z = -Math.PI / 4;
  checkmarkGroup.add(line1);

  const line2Geometry = new THREE.BoxGeometry(size * 0.4, size * 0.04, size * 0.04);
  const line2 = new THREE.Mesh(line2Geometry, checkmarkMaterial);
  line2.position.set(size * 0.05, -size * 0.1, 0);
  line2.rotation.z = Math.PI / 4;
  checkmarkGroup.add(line2);

  checkmarkGroup.scale.set(0, 0, 0);
  modelGroup.add(checkmarkGroup);

  modelGroup.scale.set(1.2, 1.2, 1.2);

  return modelGroup;
}