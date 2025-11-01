<template>
  <div id="app">
    <Toolbar />
    <Canvas />
  </div>
</template>

<script>
import Toolbar from './components/Toolbar.vue'
import Canvas from './components/Canvas.vue'

export default {
  name: 'App',
  components: {
    Toolbar,
    Canvas
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}
</style>