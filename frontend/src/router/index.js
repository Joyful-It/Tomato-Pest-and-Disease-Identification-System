/**
 * 文件名: index.js
 * 功能描述: Vue Router 路由配置 - 精简版
 * 作者: ZT
 * 日期: 2026/6/17
 */

import { createRouter, createWebHistory } from 'vue-router'

const HomeView = () => import('../views/HomeView.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
