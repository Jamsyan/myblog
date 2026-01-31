<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { Icon } from './index.js';

const props = defineProps({
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['mini', 'small', 'default', 'large'].includes(value)
  },
  placeholder: {
    type: String,
    default: '搜索...'
  },
  modelValue: {
    type: String,
    default: ''
  },
  animationDuration: {
    type: String,
    default: '1.5s'
  }
});

const emit = defineEmits(['update:modelValue', 'search']);

const handleInput = (event) => {
  emit('update:modelValue', event.target.value);
};

const handleSubmit = (event) => {
  event.preventDefault();
  emit('search');
};

const getSizeClass = () => {
  return {
    'search-input--mini': props.size === 'mini',
    'search-input--small': props.size === 'small',
    'search-input--default': props.size === 'default',
    'search-input--large': props.size === 'large'
  };
};

const isAnimated = ref(false);

onMounted(() => {
  nextTick(() => {
    isAnimated.value = true;
  });
});
</script>

<template>
  <div class="search-container">
    <form class="search-input" :class="[getSizeClass(), { 'search-input--animated': isAnimated }]"
      @submit="handleSubmit" :style="{ '--animation-duration': animationDuration }">
      <input type="text" :placeholder="placeholder" :value="modelValue" @input="handleInput"
        class="search-input__field" />
      <button type="submit" class="search-input__button">
        <Icon name="Search" :size="20" />
      </button>
    </form>
  </div>
</template>

<style scoped>
.search-container {
  width: 100%;
  overflow: hidden;
  position: relative;
}

.search-input {
  position: relative;
  display: flex;
  align-items: center;
  border-radius: var(--search-border-radius, 24px);
  background-color: var(--light-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: 
    all 0.3s ease,
    border-radius 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
  overflow: hidden;
}

.search-input:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.search-input__field {
  flex: 1;
  flex-shrink: 1;
  min-width: 80px;
  padding: 8px 12px 8px 8px;
  margin-left: 8px;
  border: none;
  border-radius: 24px;
  background-color: rgba(255, 255, 255, 0.8);
  font-size: var(--search-field-font-size, 16px);
  color: var(--text-primary);
  outline: none;
  opacity: 1;
  box-sizing: border-box;
  transition: 
    opacity 0.3s ease,
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    font-size 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    border-radius 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    margin-left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-input__field::placeholder {
  color: var(--text-secondary);
}

.search-input__button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--search-button-width, 44px);
  height: var(--search-button-height, 36px);
  margin: var(--search-button-margin, 4px);
  border: none;
  border-radius: var(--search-button-radius, 20px);
  background-color: var(--primary-color);
  color: white;
  cursor: pointer;
  transition: 
    all 0.3s ease,
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    margin 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    border-radius 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  position: relative;
  left: 0;
  transform: none;
  z-index: 10;
}

.search-input__button svg {
  display: block;
  fill: none;
  stroke: currentColor;
  width: var(--search-button-icon-size, 20px);
  height: var(--search-button-icon-size, 20px);
  transition: 
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-input__button:hover {
  background-color: var(--secondary-color);
  transform: scale(1.05);
}

.search-input--animated {
  animation: slideIn var(--animation-duration) cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes slideIn {
  0% {
    width: 0;
    transform: translateX(-100%);
    opacity: 0;
  }

  30% {
    width: 0;
    transform: translateX(0);
    opacity: 0.5;
  }

  100% {
    width: 100%;
    transform: translateX(0);
    opacity: 1;
  }
}

.search-input--small {
  --search-border-radius: 20px;
  min-width: 200px;
}

.search-input--small .search-input__field {
  padding: 6px 10px 6px 6px;
  margin-left: 6px;
  border-radius: 20px;
  font-size: 14px;
}

.search-input--small .search-input__button {
  --search-button-width: 36px;
  --search-button-height: 28px;
  --search-button-margin: 3px;
  --search-button-radius: 16px;
  --search-button-icon-size: 16px;
}

.search-input--mini {
  --search-border-radius: 16px;
  min-width: 120px;
}

.search-input--mini .search-input__field {
  padding: 4px 8px 4px 4px;
  margin-left: 4px;
  border-radius: 16px;
  font-size: 12px;
}

.search-input--mini .search-input__button {
  --search-button-width: 24px;
  --search-button-height: 24px;
  --search-button-margin: 2px;
  --search-button-radius: 12px;
  --search-button-icon-size: 12px;
}

.search-input--large {
  --search-border-radius: 28px;
}

.search-input--large .search-input__field {
  padding: 10px 14px 10px 10px;
  margin-left: 10px;
  border-radius: 28px;
  font-size: 18px;
}

.search-input--large .search-input__button {
  --search-button-width: 52px;
  --search-button-height: 40px;
  --search-button-margin: 5px;
  --search-button-radius: 24px;
  --search-button-icon-size: 24px;
}

@media (max-width: 768px) {
  .search-input--large .search-input__field {
    padding: 14px 16px 14px 14px;
    margin-left: 14px;
    border-radius: 28px;
    font-size: 16px;
  }

  .search-input--large .search-input__button {
    --search-button-width: 44px;
    --search-button-height: 36px;
    --search-button-margin: 4px;
  }

  .search-input--small {
    min-width: 150px;
  }

  .search-input--small .search-input__field {
    padding: 9px 12px 9px 9px;
    margin-left: 9px;
    border-radius: 20px;
    font-size: 13px;
  }

  .search-input--small .search-input__button {
    --search-button-width: 32px;
    --search-button-height: 24px;
    --search-button-margin: 3px;
    --search-button-radius: 12px;
    --search-button-icon-size: 14px;
  }
}
</style>