<template>
  <div class="canvas-container">
    <div ref="stageContainer" class="stage-container"></div>
  </div>
</template>

<script>
import Konva from 'konva'
import { useCanvasStore } from '../stores/canvas'

export default {
  name: 'Canvas',
  data() {
    return {
      stage: null,
      layer: null,
      cardElements: new Map(),
      noteElements: new Map(),
      linkElements: []
    }
  },
  setup() {
    const canvasStore = useCanvasStore()
    return { canvasStore }
  },
  mounted() {
    this.initCanvas()
    this.loadData()
  },
  methods: {
    initCanvas() {
      this.stage = new Konva.Stage({
        container: this.$refs.stageContainer,
        width: window.innerWidth,
        height: window.innerHeight,
        draggable: true
      })

      this.layer = new Konva.Layer()
      this.stage.add(this.layer)

      // Zoom functionality
      this.stage.on('wheel', (e) => {
        e.evt.preventDefault()
        const scaleBy = 1.1
        const oldScale = this.stage.scaleX()
        const pointer = this.stage.getPointerPosition()

        const mousePointTo = {
          x: (pointer.x - this.stage.x()) / oldScale,
          y: (pointer.y - this.stage.y()) / oldScale,
        }

        const newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy
        this.stage.scale({ x: newScale, y: newScale })

        const newPos = {
          x: pointer.x - mousePointTo.x * newScale,
          y: pointer.y - mousePointTo.y * newScale,
        }
        this.stage.position(newPos)
        this.stage.batchDraw()
      })

      // Handle window resize
      window.addEventListener('resize', this.handleResize)
    },

    handleResize() {
      this.stage.width(window.innerWidth)
      this.stage.height(window.innerHeight)
    },

    async loadData() {
      await this.canvasStore.loadData()
      this.renderCanvas()
    },

    renderCanvas() {
      this.layer.destroyChildren()

      // Render cards
      this.canvasStore.cards.forEach(card => {
        this.renderCard(card)
      })

      // Render notes
      this.canvasStore.notes.forEach(note => {
        this.renderNote(note)
      })

      // Render links
      this.renderLinks()

      this.layer.draw()
    },

    renderCard(card) {
      const group = new Konva.Group({
        x: card.x,
        y: card.y,
        draggable: true,
        id: card.id
      })

      const rect = new Konva.Rect({
        width: card.width || 300,
        height: card.height || 200,
        fill: 'lightblue',
        stroke: 'blue',
        strokeWidth: 2,
        cornerRadius: 5
      })

      const text = new Konva.Text({
        text: card.title,
        x: 10,
        y: 10,
        fontSize: 16,
        fill: 'black',
        width: card.width - 20
      })

      group.add(rect)
      group.add(text)

      // Event listeners
      group.on('click', () => {
        this.canvasStore.setSelectedElement(card)
      })

      group.on('dragend', () => {
        this.updateCardPosition(card.id, group.x(), group.y())
      })

      this.layer.add(group)
      this.cardElements.set(card.id, group)
    },

    renderNote(note) {
      const group = new Konva.Group({
        x: note.x,
        y: note.y,
        draggable: true,
        id: note.id
      })

      const rect = new Konva.Rect({
        width: note.width || 250,
        height: note.height || 150,
        fill: 'lightyellow',
        stroke: 'orange',
        strokeWidth: 2,
        cornerRadius: 5
      })

      const text = new Konva.Text({
        text: note.title,
        x: 10,
        y: 10,
        fontSize: 14,
        fill: 'black',
        width: note.width - 20
      })

      group.add(rect)
      group.add(text)

      // Event listeners
      group.on('click', () => {
        this.canvasStore.setSelectedElement(note)
      })

      group.on('dragend', () => {
        this.updateNotePosition(note.id, group.x(), group.y())
      })

      this.layer.add(group)
      this.noteElements.set(note.id, group)
    },

    renderLinks() {
      this.canvasStore.taskLinks.forEach(link => {
        const sourceCard = this.cardElements.get(link.source_id)
        const targetCard = this.cardElements.get(link.target_id)

        if (sourceCard && targetCard) {
          const line = new Konva.Line({
            points: [
              sourceCard.x() + (sourceCard.children[0].width() / 2),
              sourceCard.y() + (sourceCard.children[0].height() / 2),
              targetCard.x() + (targetCard.children[0].width() / 2),
              targetCard.y() + (targetCard.children[0].height() / 2)
            ],
            stroke: 'gray',
            strokeWidth: 2,
            dash: [5, 5]
          })

          this.layer.add(line)
          this.linkElements.push(line)
        }
      })
    },

    async updateCardPosition(cardId, x, y) {
      await this.canvasStore.updateCard(cardId, { x, y })
    },

    async updateNotePosition(noteId, x, y) {
      // TODO: Implement note update
      console.log('Update note position:', noteId, x, y)
    }
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
  }
}
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