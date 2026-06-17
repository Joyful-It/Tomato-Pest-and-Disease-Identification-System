/**
 * 文件名: main.js
 * 功能描述: Vue.js 应用入口文件
 * 作者: ZT
 * 日期: 2026/6/17
 */

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')