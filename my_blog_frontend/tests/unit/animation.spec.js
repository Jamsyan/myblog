/**
 * 动画系统单元测试
 */

import { describe, test, expect, beforeEach, vi } from 'vitest';
import { ColorEngine } from '../src/utils/colorEngine.js';
import { ParticleFlow, WaveRipple, AuroraEffect } from '../src/utils/animationAlgorithms.js';
import { animationConfig, getPreset, validateParams } from '../src/config/animationConfig.js';

describe('ColorEngine', () => {
  test('hexToRgb converts hex to rgb correctly', () => {
    const result = ColorEngine.hexToRgb('#FF0000');
    expect(result).toEqual({ r: 255, g: 0, b: 0 });
  });
  
  test('rgbToHex converts rgb to hex correctly', () => {
    const result = ColorEngine.rgbToHex(255, 0, 0);
    expect(result).toBe('#ff0000');
  });
  
  test('rgbToHsl converts rgb to hsl correctly', () => {
    const result = ColorEngine.rgbToHsl(255, 0, 0);
    expect(result.h).toBeCloseTo(0, 0);
    expect(result.s).toBeCloseTo(100, 0);
    expect(result.l).toBeCloseTo(50, 0);
  });
  
  test('hslToRgb converts hsl to rgb correctly', () => {
    const result = ColorEngine.hslToRgb(0, 100, 50);
    expect(result.r).toBeCloseTo(255, 0);
    expect(result.g).toBeCloseTo(0, 0);
    expect(result.b).toBeCloseTo(0, 0);
  });
  
  test('blendColors mixes colors correctly', () => {
    const colors = ['#FF0000', '#00FF00'];
    const weights = [0.5, 0.5];
    const result = ColorEngine.blendColors(colors, weights);
    expect(result.r).toBeCloseTo(127.5, 0);
    expect(result.g).toBeCloseTo(127.5, 0);
    expect(result.b).toBeCloseTo(0, 0);
  });
  
  test('normalizeWeights normalizes weights correctly', () => {
    const weights = [1, 1, 2];
    const normalized = ColorEngine.normalizeWeights(weights);
    expect(normalized.reduce((a, b) => a + b, 0)).toBeCloseTo(1, 5);
  });
});

describe('ParticleFlow', () => {
  let particleFlow;
  
  beforeEach(() => {
    particleFlow = new ParticleFlow({
      maxParticles: 50,
      particleSize: 2,
      speed: 1,
      colors: ['#FF0000', '#00FF00']
    });
  });
  
  test('initializes particles correctly', () => {
    expect(particleFlow.particles.length).toBe(50);
  });
  
  test('update generates valid data', () => {
    const width = 800;
    const height = 600;
    const time = 1000;
    const particles = particleFlow.update(width, height, time);
    expect(particles.length).toBe(50);
    expect(particles[0]).toHaveProperty('x');
    expect(particles[0]).toHaveProperty('y');
    expect(particles[0]).toHaveProperty('opacity');
  });
  
  test('setColors updates colors', () => {
    particleFlow.setColors(['#0000FF']);
    expect(particleFlow.colors).toEqual(['#0000FF']);
  });
});

describe('WaveRipple', () => {
  let waveRipple;
  
  beforeEach(() => {
    waveRipple = new WaveRipple({
      maxWaves: 5,
      waveSpeed: 2,
      colors: ['#0000FF']
    });
  });
  
  test('initializes waves correctly', () => {
    expect(waveRipple.waves.length).toBe(5);
  });
  
  test('update generates valid data', () => {
    const width = 800;
    const height = 600;
    const time = 1000;
    const waves = waveRipple.update(width, height, time);
    expect(waves.length).toBe(5);
    expect(waves[0]).toHaveProperty('radius');
    expect(waves[0]).toHaveProperty('opacity');
  });
});

describe('AnimationConfig', () => {
  test('getPreset returns valid preset', () => {
    const preset = getPreset('flow');
    expect(preset).toBeDefined();
    expect(preset.name).toBe('流动效果');
  });
  
  test('getPreset returns default for unknown preset', () => {
    const preset = getPreset('unknown');
    expect(preset.name).toBe('默认效果');
  });
  
  test('validateParams validates values correctly', () => {
    const config = {
      speed: { value: 1, min: 0.1, max: 2 }
    };
    const validated = validateParams({ speed: 3 }, config);
    expect(validated.speed).toBe(2);
    
    const validated2 = validateParams({ speed: 0.05 }, config);
    expect(validated2.speed).toBe(0.1);
  });
  
  test('animationConfig has required themes', () => {
    expect(animationConfig.themes['china-red']).toBeDefined();
    expect(animationConfig.themes['danqing-blue']).toBeDefined();
    expect(animationConfig.themes['fenxia-purple']).toBeDefined();
  });
  
  test('animationConfig has required presets', () => {
    expect(animationConfig.presets.default).toBeDefined();
    expect(animationConfig.presets.flow).toBeDefined();
    expect(animationConfig.presets.sparkle).toBeDefined();
  });
});

describe('Integration Tests', () => {
  test('ColorEngine palette extraction', () => {
    const mockTheme = {
      colors: {
        primary: '#D32F2F',
        secondary: '#FF7043',
        animationColors: [
          { color: '#D32F2F', weight: 0.5 },
          { color: '#FF7043', weight: 0.5 }
        ]
      }
    };
    
    const palette = ColorEngine.getThemeColorPalette(mockTheme);
    expect(palette.primary).toEqual({ r: 211, g: 47, b: 47 });
    expect(palette.animationPalette).toHaveLength(2);
  });
  
  test('ParticleFlow with custom parameters', () => {
    const flow = new ParticleFlow({
      maxParticles: 100,
      speed: 2,
      lifeTime: 100
    });
    
    expect(flow.maxParticles).toBe(100);
    expect(flow.speed).toBe(2);
    expect(flow.lifeTime).toBe(100);
  });
  
  test('Performance levels configuration', () => {
    expect(animationConfig.performance.high.pixelRatio).toBe(2);
    expect(animationConfig.performance.medium.pixelRatio).toBe(1.5);
    expect(animationConfig.performance.low.pixelRatio).toBe(1);
  });
});

describe('Performance Tests', () => {
  test('ParticleFlow update performance', () => {
    const flow = new ParticleFlow({
      maxParticles: 500,
      colors: ['#FF0000', '#00FF00', '#0000FF']
    });
    
    const startTime = performance.now();
    for (let i = 0; i < 100; i++) {
      flow.update(800, 600, i * 16);
    }
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(100);
  });
  
  test('ColorEngine blend performance', () => {
    const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00'];
    const weights = [0.25, 0.25, 0.25, 0.25];
    
    const startTime = performance.now();
    for (let i = 0; i < 1000; i++) {
      ColorEngine.blendColors(colors, weights);
    }
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(50);
  });
});
