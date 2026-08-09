<template>
  <div class="canvas-view">
    <Toolbar />
    <Canvas ref="canvas" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Toolbar from '../components/Toolbar.vue';
import Canvas from '../components/Canvas.vue';

const canvas = ref(null);

const handleAddCard = (cardData) => {
  if (canvas.value) {
    canvas.value.addCard(cardData);
  }
};

const handleAddNote = (noteData) => {
  if (canvas.value) {
    canvas.value.addNote(noteData);
  }
};

defineExpose({ handleAddCard, handleAddNote });
</script>

<style scoped>
.canvas-view {
  width: 100vw;
  height: 100vh;
}
</style>
