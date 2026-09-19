<template>
  <div id="app">
    <ThemeToggle />
    <router-view />
    <CanvasContextMenu />
  </div>
</template>

<script setup>
import ThemeToggle from './components/ThemeToggle.vue';
import CanvasContextMenu from './components/CanvasContextMenu.vue';
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}
</style>
