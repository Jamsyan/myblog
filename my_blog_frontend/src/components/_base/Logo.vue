<script setup>
const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large', 'xlarge'].includes(value)
  },
  withLink: {
    type: Boolean,
    default: true
  },
  href: {
    type: String,
    default: '/'
  }
});

const sizeClasses = {
  small: 'logo-small',
  medium: 'logo-medium',
  large: 'logo-large',
  xlarge: 'logo-xlarge'
};
</script>

<template>
  <component :is="withLink ? 'router-link' : 'div'" :to="href" class="logo-container" :class="sizeClasses[size]">
    <span class="logo-text">锦年志</span>
  </component>
</template>

<style scoped>
.logo-container {
  display: inline-block;
  text-decoration: none;
  transition: 
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-container:hover {
  transform: translateY(-2px);
}

.logo-text {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--accent-color) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  display: inline-block;
  font-size: var(--logo-font-size, 1.8rem);
  transition: 
    font-size 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-text::before {
  content: '锦年志';
  position: absolute;
  left: 0;
  top: 0;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--accent-color) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: blur(8px);
  opacity: 0.5;
  z-index: -1;
  transition: all 0.3s ease;
}

.logo-container:hover .logo-text::before {
  filter: blur(12px);
  opacity: 0.7;
}

.logo-small .logo-text {
  --logo-font-size: 1rem;
}

.logo-medium .logo-text {
  --logo-font-size: 1.8rem;
}

.logo-large .logo-text {
  --logo-font-size: 2.5rem;
}

.logo-xlarge .logo-text {
  --logo-font-size: 3.5rem;
}

@media (max-width: 768px) {
  .logo-small .logo-text {
    --logo-font-size: 0.9rem;
  }

  .logo-medium .logo-text {
    --logo-font-size: 1.5rem;
  }

  .logo-large .logo-text {
    --logo-font-size: 2rem;
  }

  .logo-xlarge .logo-text {
    --logo-font-size: 2.5rem;
  }
}
</style>
