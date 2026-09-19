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
import { useThemeStore } from '../stores/theme';

const stageContainer = ref(null);
const stage = ref(null);
const layer = ref(null);
const elementService = ref(null);
const elements = new Map();
const linkElements = [];

const canvasStore = useCanvasStore();
const themeStore = useThemeStore();

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
      if (element.updateDisplay) {
        element.updateDisplay(card);
      } else {
        element.updateLabel(card.title);
      }
    }
  });
  
  canvasStore.notes.forEach(note => {
    const element = toRaw(elements.get(note.id));
    if (element) {
      element.updatePosition(note.x, note.y);
      if (element.updateDisplay) {
        element.updateDisplay(note);
      } else {
        element.updateLabel(note.title);
      }
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

  const elementCenter = (element) => {
    const rect = element.group.children[0];
    return {
      x: element.group.x() + rect.width() / 2,
      y: element.group.y() + rect.height() / 2
    };
  };

  /** Directed edge: arrow at target (source_id → target_id). */
  const drawLinkArrow = (linkKind, linkId, sourceId, targetId, stroke, highlighted = false) => {
    const sourceElement = toRaw(elements.get(sourceId));
    const targetElement = toRaw(elements.get(targetId));
    if (sourceElement && targetElement && sourceElement.group && targetElement.group) {
      const from = elementCenter(sourceElement);
      const to = elementCenter(targetElement);
      const arrow = markRaw(new Konva.Arrow({
        points: [from.x, from.y, to.x, to.y],
        stroke: highlighted ? '#2563eb' : stroke,
        fill: highlighted ? '#2563eb' : stroke,
        strokeWidth: highlighted ? 4 : 2,
        pointerLength: highlighted ? 16 : 12,
        pointerWidth: highlighted ? 14 : 12,
        pointerAtBeginning: false,
        pointerAtEnding: true,
        dash: highlighted ? [] : [6, 4],
        listening: false,
        shadowColor: highlighted ? '#2563eb' : undefined,
        shadowBlur: highlighted ? 8 : 0,
        shadowOpacity: highlighted ? 0.45 : 0
      }));
      layer.value.add(arrow);
      if (highlighted) {
        arrow.moveToTop();
      } else {
        arrow.moveToBottom();
      }
      linkElements.push(arrow);
    }
  };

  const taskLinkEntries = canvasStore.taskLinks.map(link => ({
    kind: 'task',
    id: link.id,
    source_id: link.source_id,
    target_id: link.target_id,
    stroke: '#64748b'
  }));
  const noteLinkEntries = canvasStore.noteLinks.map(link => ({
    kind: 'note',
    id: link.id,
    source_id: link.source_id,
    target_id: link.target_id,
    stroke: '#ca8a04'
  }));
  const allLinks = [...taskLinkEntries, ...noteLinkEntries];
  const highlightKey = canvasStore.highlightedLinkKey;

  allLinks
    .filter(entry => highlightKey !== canvasStore.linkKey(entry.kind, entry.id))
    .forEach(entry => {
      drawLinkArrow(entry.kind, entry.id, entry.source_id, entry.target_id, entry.stroke, false);
    });

  allLinks
    .filter(entry => highlightKey === canvasStore.linkKey(entry.kind, entry.id))
    .forEach(entry => {
      drawLinkArrow(entry.kind, entry.id, entry.source_id, entry.target_id, entry.stroke, true);
    });
};

const applyLinkPeerHighlights = () => {
  const peerId = canvasStore.linkPeerElementId;
  const selectedId = canvasStore.selectedElement?.id;

  for (const [id, element] of elements) {
    const raw = toRaw(element);
    if (!raw?.setLinkPeerHighlight) continue;
    if (id === selectedId) {
      raw.setLinkPeerHighlight(false);
      continue;
    }
    raw.setLinkPeerHighlight(Boolean(peerId && id === peerId));
  }
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
watch(() => canvasStore.cards, () => {
  nextTick(() => renderCanvas());
}, { deep: true });

watch(() => canvasStore.notes, () => {
  nextTick(() => renderCanvas());
}, { deep: true });

watch(() => canvasStore.taskLinks.length, () => {
  nextTick(() => renderCanvas());
});

watch(() => canvasStore.noteLinks.length, () => {
  nextTick(() => renderCanvas());
});

watch(
  () => themeStore.theme,
  () => {
    nextTick(() => {
      for (const element of elements.values()) {
        const raw = toRaw(element);
        if (raw?.refreshTheme) {
          raw.refreshTheme();
        }
      }
      if (layer.value) {
        layer.value.draw();
      }
    });
  }
);

watch(
  () => [canvasStore.highlightedLinkKey, canvasStore.linkPeerElementId],
  () => {
    nextTick(() => {
      applyLinkPeerHighlights();
      renderLinks();
      if (layer.value) {
        layer.value.draw();
      }
    });
  }
);

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
  } else {
    applyLinkPeerHighlights();
    renderLinks();
  }

  if (layer.value) {
    layer.value.draw();
  }
  
  previousSelectedElement = newElement;
});

defineExpose({ addCard, addNote });

onMounted(() => {
  elementService.value = new CanvasElementService(canvasStore);
  elementService.value.setPositionHandlers({ updateCardPosition, updateNotePosition });
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
  background: var(--holst-canvas-bg);
}
</style>
