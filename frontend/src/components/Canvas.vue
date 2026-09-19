<template>
  <div class="canvas-container">
    <div ref="stageContainer" class="stage-container"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, toRaw, markRaw, watch, nextTick } from 'vue';
import Konva from 'konva';
import { NoteCard } from '../classes/NoteCard.js';
import { TaskCard } from '../classes/TaskCard.js';
import { CanvasElementService } from '../services/CanvasElementService.js';
import { useCanvasStore } from '../stores/canvas';

const stageContainer = ref(null);
const stage = ref(null);
const layer = ref(null);
const elementService = ref(null);
const elements = new Map();
const linkElements = [];

const canvasStore = useCanvasStore();

const initCanvas = () => {
  const stageObj = markRaw(new Konva.Stage({
    container: stageContainer.value,
    width: window.innerWidth,
    height: window.innerHeight,
    draggable: true
  }));

  const layerObj = markRaw(new Konva.Layer());
  stageObj.add(layerObj);
  
  stage.value = stageObj;
  layer.value = layerObj;

  // Клик по пустому месту - снять выделение
  stage.value.on('click', (e) => {
    if (e.target === stage.value) {
      canvasStore.setSelectedElement(null);
    }
  });

  // Zoom functionality
  stage.value.on('wheel', (e) => {
    e.evt.preventDefault();
    const scaleBy = 1.1;
    const oldScale = stage.value.scaleX();
    const pointer = stage.value.getPointerPosition();

    const mousePointTo = {
      x: (pointer.x - stage.value.x()) / oldScale,
      y: (pointer.y - stage.value.y()) / oldScale,
    };

    const newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy;
    stage.value.scale({ x: newScale, y: newScale });

    const newPos = {
      x: pointer.x - mousePointTo.x * newScale,
      y: pointer.y - mousePointTo.y * newScale,
    };
    stage.value.position(newPos);
    stage.value.batchDraw();
  });
};

const handleResize = () => {
  if (stage.value) {
    stage.value.width(window.innerWidth);
    stage.value.height(window.innerHeight);
  }
};

const loadData = async () => {
  await canvasStore.loadData();
  renderCanvas();
};

const renderCanvas = () => {
  updateExistingElements();
  addNewElements();
  removeDeletedElements();
  renderLinks();
  maintainElementsOrder();
  if (layer.value) {
    layer.value.draw();
  }
};

const updateExistingElements = () => {
  canvasStore.cards.forEach(card => {
    const element = toRaw(elements.get(card.id));
    if (element) {
      element.updatePosition(card.x, card.y);
    }
  });
  
  canvasStore.notes.forEach(note => {
    const element = toRaw(elements.get(note.id));
    if (element) {
      element.updatePosition(note.x, note.y);
    }
  });
};

const addNewElements = () => {
  canvasStore.cards.forEach(card => {
    if (!elements.has(card.id)) {
      createElement(card, 'task');
    }
  });
  
  canvasStore.notes.forEach(note => {
    if (!elements.has(note.id)) {
      createElement(note, 'note');
    }
  });
  
  maintainElementsOrder();
};

const removeDeletedElements = () => {
  for (let [id, element] of elements) {
    const cardExists = canvasStore.cards.some(card => card.id === id);
    const noteExists = canvasStore.notes.some(note => note.id === id);
    
    if (!cardExists && !noteExists) {
      toRaw(element).destroy();
      elements.delete(id);
    }
  }
};

const renderLinks = () => {
  linkElements.forEach(link => link.destroy());
  linkElements.length = 0;

  canvasStore.taskLinks.forEach(link => {
    const sourceElement = toRaw(elements.get(link.source_id));
    const targetElement = toRaw(elements.get(link.target_id));

    if (sourceElement && targetElement && sourceElement.group && targetElement.group) {
      const line = markRaw(new Konva.Line({
        points: [
          sourceElement.group.x() + (sourceElement.group.children[0].width() / 2),
          sourceElement.group.y() + (sourceElement.group.children[0].height() / 2),
          targetElement.group.x() + (targetElement.group.children[0].width() / 2),
          targetElement.group.y() + (targetElement.group.children[0].height() / 2)
        ],
        stroke: 'gray',
        strokeWidth: 2,
        dash: [5, 5]
      }));

      layer.value.add(line);
      line.moveToBottom();
      linkElements.push(line);
    }
  });
};

const updateCardPosition = async (cardId, x, y, zIndex) => {
  const updateData = { x, y };
  if (zIndex !== undefined) {
    updateData.z_index = zIndex;
  }
  await canvasStore.updateCard(cardId, updateData);
};

const updateNotePosition = async (noteId, x, y, zIndex) => {
  const updateData = { x, y };
  if (zIndex !== undefined) {
    updateData.z_index = zIndex;
  }
  await canvasStore.updateNote(noteId, updateData);
};

const createElement = (data, type) => {
  try {
    let element;
    
    if (type === 'task') {
      element = new TaskCard(data, elementService.value, layer.value);
    } else if (type === 'note') {
      element = new NoteCard(data, elementService.value, layer.value);
    }
    
    if (element) {
      element.layer.parent = { updateCardPosition, updateNotePosition };
      const group = element.createGroup();
      if (group && group.children && group.children.length > 0) {
        layer.value.add(group);
        elements.set(data.id, markRaw(element));
      }
    }
  } catch (error) {
    console.error('Error creating element:', error, data);
  }
};

const maintainElementsOrder = () => {
  const sortedElements = elementService.value.getSortedElements();
  
  sortedElements.forEach(data => {
    const element = toRaw(elements.get(data.id));
    if (element && element.group) {
      element.group.moveToTop();
    }
  });
};

const addCard = async (cardData) => {
  try {
    if (cardData.x === undefined || cardData.y === undefined) {
      cardData.x = 100;
      cardData.y = 100;
    }
    await canvasStore.createCard(cardData);
  } catch (error) {
    console.error('Error adding card:', error);
  }
};

const addNote = async (noteData) => {
  try {
    if (noteData.x === undefined || noteData.y === undefined) {
      noteData.x = 150;
      noteData.y = 150;
    }
    await canvasStore.createNote(noteData);
  } catch (error) {
    console.error('Error adding note:', error);
  }
};

// Watch for store changes
watch(() => canvasStore.cards.length, () => {
  nextTick(() => {
    renderCanvas();
  });
}, { deep: true });

watch(() => canvasStore.notes.length, () => {
  nextTick(() => {
    renderCanvas();
  });
}, { deep: true });

// Watch for selected element changes
let previousSelectedElement = null;
watch(() => canvasStore.selectedElement, (newElement) => {
  if (previousSelectedElement) {
    const element = toRaw(elements.get(previousSelectedElement.id));
    if (element) {
      element.removeSelection();
    }
  }

  if (newElement) {
    const element = toRaw(elements.get(newElement.id));
    if (element) {
      element.setSelected();
    }
  }

  if (layer.value) {
    layer.value.draw();
  }
  
  previousSelectedElement = newElement;
});

defineExpose({ addCard, addNote });

onMounted(() => {
  elementService.value = new CanvasElementService(canvasStore);
  initCanvas();
  loadData();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (stage.value) {
    stage.value.destroy();
  }
});
</script>

<style scoped>
.canvas-container {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.stage-container {
  width: 100%;
  height: 100%;
}
</style>
