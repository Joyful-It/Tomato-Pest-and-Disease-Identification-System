<!--
文件名: App.vue
功能描述: Vue.js 根组件 - 清新农业风格
作者: ZT
日期: 2026/6/17
-->

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  background: #f5f7f0;
  color: #333;
  min-height: 100vh;
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #8bc34a;
  border-radius: 3px;
}
</style>
