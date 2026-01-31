<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  // 按钮类型
  type: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'outline', 'text'].includes(value)
  },
  // 按钮大小
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 是否为加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 按钮图标
  icon: {
    type: String,
    default: ''
  },
  // 图标位置
  iconPosition: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'right'].includes(value)
  }
});

const emit = defineEmits(['click']);

const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event);
  }
};
</script>

<template>
  <button
    class="base-button"
    :class="{
      [`base-button--${type}`]: true,
      [`base-button--${size}`]: true,
      'base-button--disabled': disabled,
      'base-button--loading': loading
    }"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="icon && iconPosition === 'left'" class="base-button__icon">
      {{ icon }}
    </span>
    <slot></slot>
    <span v-if="icon && iconPosition === 'right'" class="base-button__icon">
      {{ icon }}
    </span>
    <span v-if="loading" class="base-button__loading">
      Loading...
    </span>
  </button>
</template>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-sans);
  font-weight: var(--font-weight-medium);
  border: none;
  border-radius: var(--border-radius-button);
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-button);
}

.base-button:hover:not(.base-button--disabled):not(.base-button--loading) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-button-hover);
}

.base-button:focus {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}

.base-button--disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.base-button--loading {
  cursor: wait;
}

/* 按钮类型 */
.base-button--primary {
  background-color: var(--primary-color);
  color: white;
}

.base-button--primary:hover:not(.base-button--disabled):not(.base-button--loading) {
  background-color: var(--primary-hover);
}

.base-button--secondary {
  background-color: var(--neutral-extra-light-gray);
  color: var(--neutral-dark-gray);
}

.base-button--secondary:hover:not(.base-button--disabled):not(.base-button--loading) {
  background-color: var(--neutral-light-gray);
}

.base-button--outline {
  background-color: transparent;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.base-button--outline:hover:not(.base-button--disabled):not(.base-button--loading) {
  background-color: var(--light-color);
}

.base-button--text {
  background-color: transparent;
  color: var(--primary-color);
  box-shadow: none;
}

.base-button--text:hover:not(.base-button--disabled):not(.base-button--loading) {
  background-color: var(--light-color);
  box-shadow: none;
}

/* 按钮大小 */
.base-button--small {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: var(--font-size-sm);
}

.base-button--medium {
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: var(--font-size-base);
}

.base-button--large {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: var(--font-size-lg);
}

/* 图标和加载状态 */
.base-button__icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.base-button__loading {
  font-size: var(--font-size-sm);
  opacity: 0.8;
}
</style>