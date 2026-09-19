<template>
  <div class="canvas-view">
    <Toolbar />
    <TaskJournal />
    <Canvas ref="canvas" />
    <EditorPanel v-if="canvasStore.selectedElement" :element="canvasStore.selectedElement" />
    <CanvasContextMenu />
    <div v-if="canvasStore.linkMode" class="link-hint">
      {{ linkHintText }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue';
import Toolbar from '../components/Toolbar.vue';
import TaskJournal from '../components/TaskJournal.vue';
import Canvas from '../components/Canvas.vue';
import EditorPanel from '../components/EditorPanel.vue';
import CanvasContextMenu from '../components/CanvasContextMenu.vue';
import { useCanvasStore } from '../stores/canvas';

const canvasStore = useCanvasStore();

const linkHintText = computed(() => {
  if (canvasStore.pendingLinkSource) {
    return 'Выберите второй элемент для связи (Esc — отмена)';
  }
  return 'Режим связи: выберите первый элемент (Esc — выход)';
});

const onKeyDown = (e) => {
  if (e.key !== 'Escape') {
    return;
  }
  if (canvasStore.linkMode) {
    canvasStore.cancelLinkMode();
    return;
  }
  if (canvasStore.contextMenu) {
    canvasStore.closeContextMenu();
    return;
  }
  if (canvasStore.selectedElement) {
    canvasStore.setSelectedElement(null);
  }
};

onMounted(() => {
  window.addEventListener('keydown', onKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown);
});
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
  background: var(--holst-hint-bg);
  color: var(--holst-hint-text);
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 1001;
  pointer-events: none;
}
</style>
