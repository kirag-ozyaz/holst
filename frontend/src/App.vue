<template>
  <div id="app">
    <ThemeToggle />
    <router-view />
  </div>
</template>

<script setup>
import ThemeToggle from './components/ThemeToggle.vue';
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}
</style>
