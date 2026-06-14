<script setup lang="ts">
</script>

<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/">🏠 首页</router-link>
      <router-link to="/items">📦 物品</router-link>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.navbar {
  display: flex;
  gap: 20px;
  justify-content: center;
  padding: 16px;
  background: #1a1a2e;
  margin-bottom: 30px;
}
.navbar a {
  color: #fff;
  text-decoration: none;
  padding: 6px 16px;
  border-radius: 6px;
  transition: background 0.2s;
}
.navbar a:hover,
.navbar a.router-link-active {
  background: #42b883;
}
main {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}
</style>
