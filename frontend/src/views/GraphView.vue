<template>
  <div class="graph-view">
    <div ref="graphContainer" class="graph-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import cytoscape from 'cytoscape';
import { useCanvasStore } from '../stores/canvas';

const graphContainer = ref(null);
const cy = ref(null);
const canvasStore = useCanvasStore();
const route = useRoute();
const router = useRouter();

const initGraph = () => {
  if (!graphContainer.value) return;
  
  cy.value = cytoscape({
    container: graphContainer.value,
    style: [
      {
        selector: 'node',
        style: {
          'background-color': '#666',
          'label': 'data(label)',
          'text-valign': 'center',
          'text-halign': 'center',
          'color': 'white',
          'font-size': '12px'
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 2,
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
          'shape': 'rectangle'
        }
      },
      {
        selector: '.note',
        style: {
          'background-color': 'lightyellow',
          'shape': 'ellipse'
        }
      }
    ],
    layout: {
      name: 'cose'
    }
  });

  cy.value.on('tap', 'node', (evt) => {
    const node = evt.target;
    console.log('Tapped node:', node.data());
  });
};

const renderGraph = () => {
  if (!cy.value) return;
  
  const elements = [];

  canvasStore.cards.forEach(card => {
    elements.push({
      data: { id: card.id, label: card.title, type: 'card' },
      classes: 'card'
    });
  });

  canvasStore.notes.forEach(note => {
    elements.push({
      data: { id: note.id, label: note.title, type: 'note' },
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

  cy.value.add(elements);
  cy.value.layout({ name: 'cose' }).run();
};

const loadData = async () => {
  await canvasStore.loadData();
  renderGraph();
};

onMounted(() => {
  initGraph();
  loadData();
});

watch(route, () => {
  if (route.path === '/graph') {
    nextTick(() => {
      loadData();
    });
  }
});

onUnmounted(() => {
  if (cy.value) {
    cy.value.destroy();
  }
});
</script>

<style scoped>
.graph-view {
  width: 100vw;
  height: 100vh;
}

.graph-container {
  width: 100%;
  height: 100%;
}
</style>
