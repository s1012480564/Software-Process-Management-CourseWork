<template>
  <div id="app">
    <!-- 如果未登录，显示登录页面 -->
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style scoped>
#app {
  font-family: Arial, Helvetica, sans-serif;
}
</style>
