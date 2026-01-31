/**
 * 路由配置文件
 */

import { createRouter, createWebHistory } from 'vue-router';
import { isAuthenticated } from '../modules/auth/services';

import LoginPage from '../modules/auth/components/LoginPage.vue';
import RegisterPage from '../modules/auth/components/RegisterPage.vue';
import HomePage from '../modules/blog/components/HomePage.vue';
import ExplorePage from '../modules/explore/components/ExplorePage.vue';
import PostDetailPage from '../modules/explore/components/PostDetailPage.vue';
import ProfilePage from '../modules/profile/components/ProfilePage.vue';

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomePage,
      meta: {
        requiresAuth: false
      }
    },
    {
      path: '/explore',
      name: 'Explore',
      component: ExplorePage,
      meta: {
        requiresAuth: false
      }
    },
    {
      path: '/explore/post/:id',
      name: 'PostDetail',
      component: PostDetailPage,
      meta: {
        requiresAuth: false
      }
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginPage,
      meta: {
        requiresAuth: false
      }
    },
    {
      path: '/register',
      name: 'Register',
      component: RegisterPage,
      meta: {
        requiresAuth: false
      }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: ProfilePage,
      meta: {
        requiresAuth: true
      }
    },
    // 404页面
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth;

  if (requiresAuth && !isAuthenticated()) {
    // 需要认证但未登录，重定向到登录页
    next('/login');
  } else {
    // 不需要认证或已登录，继续导航
    next();
  }
});

export default router;
