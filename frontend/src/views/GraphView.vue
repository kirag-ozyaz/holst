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
          'line-color': '#ccc',
          'target-arrow-color': '#ccc',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier'
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
      }
    });
  });

  canvasStore.noteLinks.forEach(link => {
    elements.push({
      data: {
        id: `note-link-${link.id}`,
        source: link.source_id,
        target: link.target_id,
        label: link.link_type
      }
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
