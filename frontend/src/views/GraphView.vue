<template>
  <div class="graph-view">
    <div ref="graphContainer" class="graph-container"></div>
  </div>
</template>

<script>
import cytoscape from 'cytoscape'
import { useCanvasStore } from '../stores/canvas'

export default {
  name: 'GraphView',
  data() {
    return {
      cy: null
    }
  },
  setup() {
    const canvasStore = useCanvasStore()
    return { canvasStore }
  },
  mounted() {
    this.initGraph()
    this.loadGraphData()
  },
  methods: {
    initGraph() {
      this.cy = cytoscape({
        container: this.$refs.graphContainer,
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
      })

      // Event listeners
      this.cy.on('tap', 'node', (evt) => {
        const node = evt.target
        console.log('Tapped node:', node.data())
      })
    },

    async loadGraphData() {
      await this.canvasStore.loadData()
      this.renderGraph()
    },

    renderGraph() {
      const elements = []

      // Add cards as nodes
      this.canvasStore.cards.forEach(card => {
        elements.push({
          data: {
            id: card.id,
            label: card.title,
            type: 'card'
          },
          classes: 'card'
        })
      })

      // Add notes as nodes
      this.canvasStore.notes.forEach(note => {
        elements.push({
          data: {
            id: note.id,
            label: note.title,
            type: 'note'
          },
          classes: 'note'
        })
      })

      // Add task links as edges
      this.canvasStore.taskLinks.forEach(link => {
        elements.push({
          data: {
            id: `task-link-${link.id}`,
            source: link.source_id,
            target: link.target_id,
            label: link.link_type
          }
        })
      })

      // Add note links as edges
      this.canvasStore.noteLinks.forEach(link => {
        elements.push({
          data: {
            id: `note-link-${link.id}`,
            source: link.source_id,
            target: link.target_id,
            label: link.link_type
          }
        })
      })

      this.cy.add(elements)
      this.cy.layout({ name: 'cose' }).run()
    }
  }
}
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