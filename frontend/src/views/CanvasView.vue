<template>
  <div class="canvas-view">
    <Toolbar @add-card="handleAddCard" @add-note="handleAddNote" />
    <Canvas ref="canvas" />
    <EditorPanel v-if="canvasStore.selectedElement" :element="canvasStore.selectedElement" />
    <div v-if="canvasStore.linkMode" class="link-hint">
      {{ linkHintText }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import Toolbar from '../components/Toolbar.vue';
import Canvas from '../components/Canvas.vue';
import EditorPanel from '../components/EditorPanel.vue';
import { useCanvasStore } from '../stores/canvas';

const canvas = ref(null);
const canvasStore = useCanvasStore();

const linkHintText = computed(() => {
  if (canvasStore.pendingLinkSource) {
    return 'Выберите второй элемент для связи (Esc — отмена)';
  }
  return 'Режим связи: выберите первый элемент (Esc — выход)';
});

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

const onKeyDown = (e) => {
  if (e.key === 'Escape' && canvasStore.linkMode) {
    canvasStore.cancelLinkMode();
  }
};

onMounted(() => {
  window.addEventListener('keydown', onKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown);
});

defineExpose({ handleAddCard, handleAddNote });
</script>

<style scoped>
.canvas-view {
  width: 100vw;
  height: 100vh;
  position: relative;
}

.link-hint {
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: #1e293b;
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 1001;
  pointer-events: none;
}
</style>
