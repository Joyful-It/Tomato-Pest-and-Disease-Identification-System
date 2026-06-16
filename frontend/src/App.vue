<!--
文件名: App.vue
功能描述: Vue.js 根组件，定义应用布局
作者: ZT
日期: 2026/6/16
-->

<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-success">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="bi bi-flower1"></i> 番茄病虫害识别系统
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">
                <i class="bi bi-house"></i> 首页
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/history">
                <i class="bi bi-clock-history"></i> 历史记录
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/profile">
                <i class="bi bi-person"></i> 用户档案
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="container py-4">
      <router-view />
    </main>

    <!-- 页脚 -->
    <footer class="bg-light py-3 mt-5">
      <div class="container text-center text-muted">
        <p class="mb-0">番茄病虫害识别系统 &copy; 2026 | 技术支持：AI 智能诊断</p>
      </div>
    </footer>
  </div>
</template>

<script>
/**
 * 根组件
 * 定义应用的整体布局结构
 */
export default {
  name: 'App'
}
</script>

<style>
/* 全局样式 */
body {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  background-color: #f5f5f5;
}

.navbar-brand {
  font-weight: bold;
  font-size: 1.3rem;
}

main {
  min-height: calc(100vh - 200px);
}
</style>
