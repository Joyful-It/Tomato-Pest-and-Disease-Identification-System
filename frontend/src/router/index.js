/**
 * 文件名: index.js
 * 功能描述: Vue Router 路由配置
 * 作者: ZT
 * 日期: 2026/6/16
 */

import { createRouter, createWebHistory } from 'vue-router'

// 路由组件懒加载
const HomeView = () => import('../views/HomeView.vue')
const ResultView = () => import('../views/ResultView.vue')
const HistoryView = () => import('../views/HistoryView.vue')
const ProfileView = () => import('../views/ProfileView.vue')

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { title: '首页' }
  },
  {
    path: '/result/:id',
    name: 'Result',
    component: ResultView,
    meta: { title: '诊断结果' }
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryView,
    meta: { title: '历史记录' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { title: '用户档案' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title} - 番茄病虫害识别系统` || '番茄病虫害识别系统'
  next()
})

export default router
