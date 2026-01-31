<script setup>
import { computed, ref, provide, watch } from 'vue';
import { useRoute } from 'vue-router';
import { isAuthenticated } from './modules/auth/services/authService';
import Navbar from './components/_base/Navbar.vue';
import Footer from './components/_base/Footer.vue';
import AnimationBackground from './components/_base/AnimationBackground.vue';
import { Logo, UserAvatar } from './components/_base/index.js';
import { provideNavbarContext } from './components/_base/navbarContext.js';

const route = useRoute();

const isSplit = ref(false);

watch(route, () => {
  isSplit.value = false;
});

const triggerSplitAnimation = () => {
  if (!isSplit.value) {
    isSplit.value = true;
  }
};

provide('triggerSplit', triggerSplitAnimation);
provide('isSplit', isSplit);

const navbarContext = provideNavbarContext();

const publicRoutes = ['/', '/explore'];

const isNavbarCollapsed = computed(() => {
  return !publicRoutes.includes(route.path);
});

const mainContentMarginTop = computed(() => {
  return isNavbarCollapsed.value ? '60px' : '100px';
});
</script>

<template>
  <AnimationBackground preset="flow" />
  <Navbar />
  <main class="main-content">
    <router-view />
  </main>
  <Footer />
</template>

<style scoped>
.main-content {
  margin-top: v-bind(mainContentMarginTop);
  min-height: calc(100vh - 200px);
  transition: margin-top 0.3s ease;
}
</style>
