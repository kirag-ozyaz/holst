<template>
  <div class="canvas-view">
    <Toolbar />
    <Canvas />
  </div>
</template>

<script>
import Toolbar from '../components/Toolbar.vue'
import Canvas from '../components/Canvas.vue'

export default {
  name: 'CanvasView',
  components: {
    Toolbar,
    Canvas
  }
}
</script>

<style scoped>
.canvas-view {
  width: 100vw;
  height: 100vh;
}
</style>