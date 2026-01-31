# UI设计规范

## 1. 设计原则

### 1.1 一致性

- **视觉一致性**：所有页面使用统一的色彩、字体和间距
- **交互一致性**：相似的操作使用相似的交互方式
- **语言一致性**：使用统一的术语和表达方式

### 1.2 可用性

- **易学性**：新用户能够快速上手
- **效率性**：熟练用户能够高效操作
- **容错性**：操作错误时能够恢复或撤销

### 1.3 美观性

- **简洁性**：界面简洁，避免冗余元素
- **层次性**：信息层次清晰，重点突出
- **美观性**：视觉设计美观，符合审美标准

## 2. 组件设计规范

### 2.1 按钮组件

#### 主要按钮

```css
.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--secondary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  transform: none;
}
```

#### 次要按钮

```css
.btn-secondary {
  background-color: transparent;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
  border-radius: 20px;
  padding: 10px 22px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--primary-color);
  color: white;
}
```

### 2.2 卡片组件

```css
.card {
  background-color: white;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.card__header {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 16px;
}

.card__body {
  font-size: 16px;
  color: var(--text-color);
  line-height: 1.6;
}

.card__footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}
```

### 2.3 输入框组件

```css
.input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 16px;
  font-size: 16px;
  color: var(--text-color);
  transition: all 0.2s ease;
}

.input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(198, 40, 40, 0.1);
}

.input::placeholder {
  color: #999;
}

.input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.input--error {
  border-color: #F44336;
}

.input--error:focus {
  box-shadow: 0 0 0 3px rgba(244, 67, 54, 0.1);
}
```

### 2.4 导航组件

```css
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  z-index: 1000;
}

.nav__logo {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
}

.nav__menu {
  display: flex;
  gap: 24px;
}

.nav__item {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-color);
  text-decoration: none;
  transition: color 0.2s ease;
}

.nav__item:hover,
.nav__item--active {
  color: var(--primary-color);
}
```

## 3. 布局设计规范

### 3.1 网格系统

```css
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -8px;
}

.col {
  flex: 1;
  padding: 0 8px;
}

.col--1 { flex: 0 0 8.333333%; }
.col--2 { flex: 0 0 16.666667%; }
.col--3 { flex: 0 0 25%; }
.col--4 { flex: 0 0 33.333333%; }
.col--6 { flex: 0 0 50%; }
.col--8 { flex: 0 0 66.666667%; }
.col--12 { flex: 0 0 100%; }
```

### 3.2 间距系统

```css
:root {
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
}

/* 使用示例 */
.element {
  padding: var(--spacing-md);
  margin: var(--spacing-lg);
}
```

### 3.3 响应式断点

```css
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
}

@media (max-width: 640px) {
  /* 小屏幕样式 */
}

@media (min-width: 641px) and (max-width: 768px) {
  /* 中屏幕样式 */
}

@media (min-width: 769px) and (max-width: 1024px) {
  /* 大屏幕样式 */
}

@media (min-width: 1025px) {
  /* 超大屏幕样式 */
}
```

## 4. 字体设计规范

### 4.1 字体族

```css
:root {
  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
                       'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  --font-family-mono: 'SF Mono', Monaco, Inconsolata, 
                       'Roboto Mono', Consolas, 'Courier New', monospace;
}

body {
  font-family: var(--font-family-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### 4.2 字号层级

```css
:root {
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;
  --font-size-4xl: 36px;
}

h1 { font-size: var(--font-size-4xl); font-weight: 700; }
h2 { font-size: var(--font-size-3xl); font-weight: 700; }
h3 { font-size: var(--font-size-2xl); font-weight: 600; }
h4 { font-size: var(--font-size-xl); font-weight: 600; }
h5 { font-size: var(--font-size-lg); font-weight: 500; }
h6 { font-size: var(--font-size-base); font-weight: 500; }
```

### 4.3 行高

```css
:root {
  --line-height-tight: 1.25;
  --line-height-snug: 1.375;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.625;
  --line-height-loose: 2;
}

body {
  line-height: var(--line-height-normal);
}
```

## 5. 图标设计规范

### 5.1 图标使用

```vue
<template>
  <!-- 使用SVG图标 -->
  <svg class="icon" viewBox="0 0 24 24">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
  </svg>
</template>

<style scoped>
.icon {
  width: 24px;
  height: 24px;
  fill: currentColor;
}
</style>
```

### 5.2 图标尺寸

```css
:root {
  --icon-size-xs: 16px;
  --icon-size-sm: 20px;
  --icon-size-md: 24px;
  --icon-size-lg: 32px;
  --icon-size-xl: 40px;
}

.icon--xs { width: var(--icon-size-xs); height: var(--icon-size-xs); }
.icon--sm { width: var(--icon-size-sm); height: var(--icon-size-sm); }
.icon--md { width: var(--icon-size-md); height: var(--icon-size-md); }
.icon--lg { width: var(--icon-size-lg); height: var(--icon-size-lg); }
.icon--xl { width: var(--icon-size-xl); height: var(--icon-size-xl); }
```

## 6. 动画设计规范

### 6.1 过渡效果

```css
:root {
  --transition-fast: 0.15s ease;
  --transition-normal: 0.2s ease;
  --transition-slow: 0.3s ease;
}

.element {
  transition: all var(--transition-normal);
}
```

### 6.2 动画缓动函数

```css
:root {
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
}

.element {
  transition: transform var(--transition-normal) var(--ease-in-out);
}
```

### 6.3 常用动画

```css
/* 淡入淡出 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* 滑入滑出 */
@keyframes slideIn {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

/* 缩放 */
@keyframes scaleIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

/* 使用示例 */
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}
```

## 7. 状态设计规范

### 7.1 加载状态

```vue
<template>
  <div class="loading-container">
    <div class="loading-spinner"></div>
    <p class="loading-text">加载中...</p>
  </div>
</template>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 16px;
  color: var(--text-color);
  font-size: 14px;
}
</style>
```

### 7.2 错误状态

```vue
<template>
  <div class="error-container">
    <div class="error-icon">⚠️</div>
    <h3 class="error-title">出错了</h3>
    <p class="error-message">{{ errorMessage }}</p>
    <button class="error-button" @click="retry">重试</button>
  </div>
</template>

<style scoped>
.error-container {
  text-align: center;
  padding: 40px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 8px;
}

.error-message {
  font-size: 16px;
  color: #666;
  margin-bottom: 24px;
}

.error-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
}
</style>
```

### 7.3 空状态

```vue
<template>
  <div class="empty-container">
    <div class="empty-icon">📭</div>
    <h3 class="empty-title">暂无数据</h3>
    <p class="empty-description">{{ description }}</p>
  </div>
</template>

<style scoped>
.empty-container {
  text-align: center;
  padding: 60px 40px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 8px;
}

.empty-description {
  font-size: 16px;
  color: #666;
}
</style>
```

## 8. 无障碍设计

### 8.1 键盘导航

```vue
<template>
  <button 
    class="button"
    @click="handleClick"
    @keydown.enter="handleClick"
    :tabindex="0"
  >
    点击我
  </button>
</template>
```

### 8.2 屏幕阅读器

```vue
<template>
  <button aria-label="关闭对话框" @click="close">
    <span aria-hidden="true">×</span>
  </button>
</template>
```

### 8.3 颜色对比度

确保文本与背景的对比度至少为4.5:1（WCAG AA标准）

```css
/* 好的对比度 */
.good-contrast {
  color: #000000;
  background-color: #FFFFFF;
}

/* 差的对比度 */
.bad-contrast {
  color: #CCCCCC;
  background-color: #DDDDDD;
}
```

## 9. 设计资源

### 9.1 设计工具

- **Figma**：界面设计和原型制作
- **Sketch**：Mac平台设计工具
- **Adobe XD**：Adobe设计工具
- **Photoshop**：图片处理

### 9.2 图标资源

- **IconFont**：阿里巴巴矢量图标库
- **Feather Icons**：简洁的图标库
- **Heroicons**：Tailwind CSS图标库

### 9.3 设计规范参考

- **Material Design**：Google设计规范
- **Ant Design**：蚂蚁金服设计规范
- **Apple Human Interface**：Apple设计规范

---

**文档版本**：v1.0.0  
**最后更新**：2026-01-29  
**维护者**：MyBlog开发团队