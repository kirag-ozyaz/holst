<template>
  <div class="graph-view">
    <Toolbar />
    <div ref="graphContainer" class="graph-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import cytoscape from 'cytoscape';
import Toolbar from '../components/Toolbar.vue';
import { useCanvasStore } from '../stores/canvas';

const graphContainer = ref(null);
const cy = ref(null);
const canvasStore = useCanvasStore();
const route = useRoute();

const initGraph = () => {
  if (!graphContainer.value || cy.value) return;

  cy.value = cytoscape({
    container: graphContainer.value,
    style: [
      {
        selector: 'node',
        style: {
          'background-color': '#666',
          label: 'data(label)',
          'text-valign': 'center',
          'text-halign': 'center',
          color: 'white',
          'font-size': '12px'
        }
      },
      {
        selector: 'edge',
        style: {
          width: 2,
          'line-color': '#64748b',
          'target-arrow-color': '#64748b',
          'target-arrow-shape': 'triangle',
          'arrow-scale': 1.2,
          'curve-style': 'bezier'
        }
      },
      {
        selector: 'edge.note-edge',
        style: {
          'line-color': '#ca8a04',
          'target-arrow-color': '#ca8a04'
        }
      },
      {
        selector: '.card',
        style: {
          'background-color': 'lightblue',
          shape: 'rectangle'
        }
      },
      {
        selector: '.note',
        style: {
          'background-color': 'lightyellow',
          shape: 'ellipse'
        }
      }
    ],
    layout: { name: 'preset' }
  });
};

const buildGraphElements = () => {
  const elements = [];

  canvasStore.cards.forEach(card => {
    elements.push({
      data: { id: card.id, label: card.title || 'Задача' },
      classes: 'card'
    });
  });

  canvasStore.notes.forEach(note => {
    elements.push({
      data: { id: note.id, label: note.title || 'Заметка' },
      classes: 'note'
    });
  });

  canvasStore.taskLinks.forEach(link => {
    elements.push({
      data: {
        id: `task-link-${link.id}`,
        source: link.source_id,
        target: link.target_id,
        label: link.link_type
      },
      classes: 'task-edge'
    });
  });

  canvasStore.noteLinks.forEach(link => {
    elements.push({
      data: {
        id: `note-link-${link.id}`,
        source: link.source_id,
        target: link.target_id,
        label: link.link_type
      },
      classes: 'note-edge'
    });
  });

  return elements;
};

const renderGraph = () => {
  if (!cy.value) return;

  cy.value.elements().remove();
  cy.value.add(buildGraphElements());
  cy.value.layout({ name: 'cose', animate: false }).run();
};

const loadData = async () => {
  await canvasStore.loadData();
  renderGraph();
};

onMounted(() => {
  initGraph();
  loadData();
});

watch(
  () => route.path,
  (path) => {
    if (path === '/graph') {
      nextTick(() => {
        if (!cy.value) {
          initGraph();
        }
        loadData();
      });
    }
  }
);

watch(
  () => [canvasStore.cards.length, canvasStore.notes.length, canvasStore.taskLinks.length, canvasStore.noteLinks.length],
  () => {
    if (route.path === '/graph' && cy.value) {
      nextTick(() => renderGraph());
    }
  }
);

onUnmounted(() => {
  if (cy.value) {
    cy.value.destroy();
    cy.value = null;
  }
});
</script>

<style scoped>
.graph-view {
  width: 100vw;
  height: 100vh;
  position: relative;
}

.graph-container {
  width: 100%;
  height: calc(100vh - 56px);
  margin-top: 56px;
}
</style>
