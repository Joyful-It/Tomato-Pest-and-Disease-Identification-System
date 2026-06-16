/**
 * 文件名: main.js
 * 功能描述: Vue.js 应用入口文件
 * 作者: ZT
 * 日期: 2026/6/16
 */

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles.css'

// 创建 Vue 应用
const app = createApp(App)

// 使用路由
app.use(router)

// 挂载应用
app.mount('#app')