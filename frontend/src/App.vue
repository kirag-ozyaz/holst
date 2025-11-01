<template>
  <div id="app">
    <Toolbar @add-card="handleAddCard" @add-note="handleAddNote" />
    <Canvas ref="canvas" />
 </div>
</template>

<script>
import Canvas from './components/Canvas.vue';
import Toolbar from './components/Toolbar.vue';

export default {
  name: 'App',
  components: {
    Toolbar,
    Canvas
  },
  methods: {
    handleAddCard(cardData) {
      this.$refs.canvas.addCard(cardData)
    },
    handleAddNote(noteData) {
      this.$refs.canvas.addNote(noteData)
    }
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