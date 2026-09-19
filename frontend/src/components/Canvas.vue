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
import { CARD_MIN_HEIGHT, CARD_MIN_WIDTH } from '../utils/cardDimensions.js';

const stageContainer = ref(null);
const stage = ref(null);
const layer = ref(null);
const elementService = ref(null);
const elements = new Map();
const linkElements = [];
const transformer = ref(null);

const canvasStore = useCanvasStore();
const themeStore = useThemeStore();

const PANEL_WIDTH = 360;
const PANEL_GAP = 12;

const syncStageTransformToStore = () => {
  if (!stage.value) return;
  canvasStore.setTransform(stage.value.scaleX(), stage.value.x(), stage.value.y());
};

const publishEditorAnchor = (elementId) => {
  if (!elementId || !stage.value || !stageContainer.value) {
    return;
  }
  const element = toRaw(elements.get(elementId));
  if (!element?.group) {
    return;
  }
  const rect = element.group.children[0];
  if (!rect) {
    return;
  }
  const transform = element.group.getAbsoluteTransform();
  const topLeft = transform.point({ x: 0, y: 0 });
  const bottomRight = transform.point({ x: rect.width(), y: rect.height() });
  const containerRect = stageContainer.value.getBoundingClientRect();
  const cardLeft = containerRect.left + topLeft.x;
  const cardTop = containerRect.top + topLeft.y;
  const cardWidth = bottomRight.x - topLeft.x;
  const cardHeight = bottomRight.y - topLeft.y;

  let panelLeft = cardLeft + cardWidth + PANEL_GAP;
  if (panelLeft + PANEL_WIDTH > window.innerWidth - 8) {
    panelLeft = cardLeft - PANEL_WIDTH - PANEL_GAP;
  }
  panelLeft = Math.max(8, Math.min(panelLeft, window.innerWidth - PANEL_WIDTH - 8));
  const panelTop = Math.max(56, Math.min(cardTop, window.innerHeight - 120));

  canvasStore.setEditorAnchor({
    left: panelLeft,
    top: panelTop,
    cardLeft,
    cardTop,
    cardWidth,
    cardHeight
  });
};

const initCanvas = () => {
  const stageObj = markRaw(new Konva.Stage({
    container: stageContainer.value,
    width: window.innerWidth,
    height: window.innerHeight,
    draggable: true
  }));

  const layerObj = markRaw(new Konva.Layer());
  stageObj.add(layerObj);

  const tr = markRaw(new Konva.Transformer({
    rotateEnabled: false,
    keepRatio: false,
    enabledAnchors: [
      'top-left',
      'top-right',
      'bottom-left',
      'bottom-right',
      'middle-left',
      'middle-right',
      'top-center',
      'bottom-center'
    ],
    boundBoxFunc: (oldBox, newBox) => {
      if (newBox.width < CARD_MIN_WIDTH || newBox.height < CARD_MIN_HEIGHT) {
        return oldBox;
      }
      return newBox;
    }
  }));
  tr.on('transformend', onTransformEnd);
  layerObj.add(tr);
  transformer.value = tr;
  
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
    syncStageTransformToStore();
    if (canvasStore.selectedElement?.id) {
      publishEditorAnchor(canvasStore.selectedElement.id);
    }
  });

  stage.value.on('dragmove dragend', () => {
    syncStageTransformToStore();
    if (canvasStore.selectedElement?.id) {
      publishEditorAnchor(canvasStore.selectedElement.id);
    }
  });
};

const handleResize = () => {
  if (stage.value) {
    stage.value.width(window.innerWidth);
    stage.value.height(window.innerHeight);
  }
  if (canvasStore.selectedElement?.id) {
    publishEditorAnchor(canvasStore.selectedElement.id);
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
  maintainElementsOrder();
  renderLinks();
  if (layer.value) {
    layer.value.draw();
  }
};

const updateExistingElements = () => {
  canvasStore.cards.forEach(card => {
    const element = toRaw(elements.get(card.id));
    if (element) {
      element.updatePosition(card.x, card.y);
      const sizeChanged =
        card.width !== element.data.width || card.height !== element.data.height;
      if (element.updateDisplay && (sizeChanged || card.title !== element.data.title)) {
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
      const sizeChanged =
        note.width !== element.data.width || note.height !== element.data.height;
      if (element.updateDisplay && (sizeChanged || note.title !== element.data.title)) {
        element.updateDisplay(note);
      } else {
        element.updateLabel(note.title);
      }
    }
  });
  syncTransformerNodes();
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

/** Point on rect border from center toward (towardX, towardY). */
const rectEdgePoint = (element, towardX, towardY) => {
  const shape = element.group.children[0];
  const hw = shape.width() / 2;
  const hh = shape.height() / 2;
  const cx = element.group.x() + hw;
  const cy = element.group.y() + hh;
  const dx = towardX - cx;
  const dy = towardY - cy;
  if (dx === 0 && dy === 0) {
    return { x: cx, y: cy };
  }
  const t = Math.min(hw / Math.abs(dx), hh / Math.abs(dy));
  return { x: cx + dx * t, y: cy + dy * t };
};

const linkEndpoints = (sourceElement, targetElement, pointerLength) => {
  const sourceShape = sourceElement.group.children[0];
  const targetShape = targetElement.group.children[0];
  const sourceCx = sourceElement.group.x() + sourceShape.width() / 2;
  const sourceCy = sourceElement.group.y() + sourceShape.height() / 2;
  const targetCx = targetElement.group.x() + targetShape.width() / 2;
  const targetCy = targetElement.group.y() + targetShape.height() / 2;

  const span = Math.hypot(targetCx - sourceCx, targetCy - sourceCy) || 1;
  const fx = (targetCx - sourceCx) / span;
  const fy = (targetCy - sourceCy) / span;

  const fromBase = rectEdgePoint(sourceElement, targetCx, targetCy);
  const toBase = rectEdgePoint(targetElement, sourceCx, sourceCy);
  const tipPadding = Math.max(pointerLength * 0.55, 8);

  return {
    from: { x: fromBase.x + fx * 2, y: fromBase.y + fy * 2 },
    to: { x: toBase.x - fx * tipPadding, y: toBase.y - fy * tipPadding }
  };
};

const renderLinks = () => {
  linkElements.forEach(link => link.destroy());
  linkElements.length = 0;

  /** Directed edge: arrow at target (source_id → target_id). */
  const drawLinkArrow = (linkKind, linkId, sourceId, targetId, stroke, highlighted = false) => {
    const sourceElement = toRaw(elements.get(sourceId));
    const targetElement = toRaw(elements.get(targetId));
    if (sourceElement && targetElement && sourceElement.group && targetElement.group) {
      const pointerLength = highlighted ? 16 : 12;
      const { from, to } = linkEndpoints(sourceElement, targetElement, pointerLength);
      const arrow = markRaw(new Konva.Arrow({
        points: [from.x, from.y, to.x, to.y],
        stroke: highlighted ? '#2563eb' : stroke,
        fill: highlighted ? '#2563eb' : stroke,
        strokeWidth: highlighted ? 4 : 2.5,
        pointerLength,
        pointerWidth: highlighted ? 14 : 12,
        pointerAtBeginning: false,
        pointerAtEnding: true,
        dash: highlighted ? [] : [6, 4],
        listening: false,
        perfectDrawEnabled: false,
        shadowColor: highlighted ? '#2563eb' : undefined,
        shadowBlur: highlighted ? 8 : 0,
        shadowOpacity: highlighted ? 0.45 : 0
      }));
      layer.value.add(arrow);
      if (highlighted) {
        arrow.moveToTop();
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

const updateCardDimensions = async (cardId, width, height, zIndex) => {
  const updateData = { width, height };
  if (zIndex !== undefined) {
    updateData.z_index = zIndex;
  }
  await canvasStore.updateCard(cardId, updateData);
  nextTick(() => renderLinks());
};

const updateNoteDimensions = async (noteId, width, height, zIndex) => {
  const updateData = { width, height };
  if (zIndex !== undefined) {
    updateData.z_index = zIndex;
  }
  await canvasStore.updateNote(noteId, updateData);
  nextTick(() => renderLinks());
};

const syncTransformerNodes = () => {
  const tr = transformer.value;
  if (!tr) {
    return;
  }
  const selected = canvasStore.selectedElement;
  if (!selected || canvasStore.linkMode) {
    tr.nodes([]);
    tr.getLayer()?.batchDraw();
    return;
  }
  const element = toRaw(elements.get(selected.id));
  if (element?.group) {
    tr.nodes([element.group]);
    tr.moveToTop();
  } else {
    tr.nodes([]);
  }
  tr.getLayer()?.batchDraw();
};

const onTransformEnd = () => {
  const tr = transformer.value;
  if (!tr) {
    return;
  }
  const node = tr.nodes()[0];
  if (!node) {
    return;
  }
  const element = toRaw(elements.get(node.id()));
  if (!element?.finalizeResizeFromTransform) {
    return;
  }
  const size = element.finalizeResizeFromTransform();
  if (!size) {
    return;
  }
  const zIndex = element.data.z_index;
  const handlers = elementService.value?.positionHandlers;
  if (element.getType() === 'task') {
    if (handlers?.updateCardDimensions) {
      handlers.updateCardDimensions(element.id, size.width, size.height, zIndex);
    } else {
      canvasStore.updateCard(element.id, { width: size.width, height: size.height, z_index: zIndex });
    }
  } else if (handlers?.updateNoteDimensions) {
    handlers.updateNoteDimensions(element.id, size.width, size.height, zIndex);
  } else {
    canvasStore.updateNote(element.id, { width: size.width, height: size.height, z_index: zIndex });
  }
  nextTick(() => renderLinks());
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
    nextTick(() => publishEditorAnchor(newElement.id));
  } else {
    applyLinkPeerHighlights();
    renderLinks();
  }

  syncTransformerNodes();

  if (layer.value) {
    layer.value.draw();
  }
  
  previousSelectedElement = newElement;
});

watch(
  () => canvasStore.linkMode,
  () => {
    syncTransformerNodes();
  }
);

defineExpose({ addCard, addNote });

onMounted(() => {
  elementService.value = new CanvasElementService(canvasStore);
  elementService.value.setPositionHandlers({
    updateCardPosition,
    updateNotePosition,
    updateCardDimensions,
    updateNoteDimensions
  });
  elementService.value.setContextMenuHandler((clientX, clientY, element, previousSelection) => {
    canvasStore.openContextMenu(clientX, clientY, element, previousSelection);
  });
  elementService.value.setEditorAnchorRequest(publishEditorAnchor);
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
