<script setup>
import { computed } from 'vue';
import * as LucideIcons from 'lucide-vue-next';

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: [Number, String],
    default: 24
  },
  color: {
    type: String,
    default: 'currentColor'
  },
  strokeWidth: {
    type: Number,
    default: 2
  },
  spin: {
    type: Boolean,
    default: false
  }
});

const iconComponent = computed(() => {
  return LucideIcons[props.name];
});
</script>

<template>
  <component
    v-if="iconComponent"
    :is="iconComponent"
    :size="size"
    :color="color"
    :stroke-width="strokeWidth"
    :class="{ 'icon-spin': spin }"
  />
</template>

<style scoped>
.icon-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>