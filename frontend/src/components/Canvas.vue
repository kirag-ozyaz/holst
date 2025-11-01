<template>
  <div class="canvas-container">
    <div ref="stageContainer" class="stage-container"></div>
  </div>
</template>

<script>
import Konva from 'konva';
import { useCanvasStore } from '../stores/canvas';

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
    // Watch for changes in cards and notes
    this.canvasStore.$subscribe((mutation, state) => {
      this.$nextTick(() => {
        this.updateExistingElements();
        this.addNewElements();
        this.removeDeletedElements();
        this.renderLinks();
        this.layer.draw();
      })
    })
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

    async addCard(cardData) {
      try {
        // Если в хранилище есть карточки, определяем позицию рядом с последней
        if (this.canvasStore.cards.length > 0) {
          const lastCard = this.canvasStore.cards[this.canvasStore.cards.length - 1]
          cardData.x = lastCard.x + 50 // Смещаем на 50 пикселей вправо
          cardData.y = lastCard.y + 50  // Смещаем на 50 пикселей вниз
        } else {
          // Если карточек нет, используем случайную позицию
          cardData.x = Math.random() * 500
          cardData.y = Math.random() * 500
        }
        
        const newCard = await this.canvasStore.createCard(cardData)
        this.renderCard(newCard)
        this.layer.draw()
      } catch (error) {
        console.error('Error adding card:', error)
      }
    },

    async addNote(noteData) {
      try {
        // Если в хранилище есть заметки, определяем позицию рядом с последней
        if (this.canvasStore.notes.length > 0) {
          const lastNote = this.canvasStore.notes[this.canvasStore.notes.length - 1]
          noteData.x = lastNote.x + 50 // Смещаем на 50 пикселей вправо
          noteData.y = lastNote.y + 50  // Смещаем на 50 пикселей вниз
        } else {
          // Если заметок нет, используем случайную позицию
          noteData.x = Math.random() * 500
          noteData.y = Math.random() * 500
        }
        
        const newNote = await this.canvasStore.createNote(noteData)
        this.renderNote(newNote)
        this.layer.draw()
      } catch (error) {
        console.error('Error adding note:', error)
      }
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
      // Сначала обновляем существующие элементы
      this.updateExistingElements();
      
      // Затем добавляем новые элементы
      this.addNewElements();
      
      // Удаляем удаленные элементы
      this.removeDeletedElements();
      
      // Рендерим связи
      this.renderLinks();
      
      this.layer.draw();
    },
    
    updateExistingElements() {
      // Обновляем позиции существующих карточек
      this.canvasStore.cards.forEach(card => {
        const existingCard = this.cardElements.get(card.id);
        if (existingCard) {
          // Обновляем позицию существующего элемента
          existingCard.position({ x: card.x, y: card.y });
          // Обновляем текст
          const text = existingCard.findOne('Text');
          if (text) {
            text.text(card.title);
          }
          // Обновляем размеры
          const rect = existingCard.findOne('Rect');
          if (rect) {
            rect.width(card.width || 300);
            rect.height(card.height || 200);
          }
        }
      });
      
      // Обновляем позиции существующих заметок
      this.canvasStore.notes.forEach(note => {
        const existingNote = this.noteElements.get(note.id);
        if (existingNote) {
          // Обновляем позицию существующего элемента
          existingNote.position({ x: note.x, y: note.y });
          // Обновляем текст
          const text = existingNote.findOne('Text');
          if (text) {
            text.text(note.title);
          }
          // Обновляем размеры
          const rect = existingNote.findOne('Rect');
          if (rect) {
            rect.width(note.width || 250);
            rect.height(note.height || 150);
          }
        }
      });
    },
    
    addNewElements() {
      // Добавляем новые карточки
      this.canvasStore.cards.forEach(card => {
        if (!this.cardElements.has(card.id)) {
          this.renderCard(card);
        }
      });
      
      // Добавляем новые заметки
      this.canvasStore.notes.forEach(note => {
        if (!this.noteElements.has(note.id)) {
          this.renderNote(note);
        }
      });
    },
    
    removeDeletedElements() {
      // Удаляем карточки, которых больше нет в хранилище
      for (let [id, element] of this.cardElements) {
        const exists = this.canvasStore.cards.some(card => card.id === id);
        if (!exists) {
          element.destroy();
          this.cardElements.delete(id);
        }
      }
      
      // Удаляем заметки, которых больше нет в хранилище
      for (let [id, element] of this.noteElements) {
        const exists = this.canvasStore.notes.some(note => note.id === id);
        if (!exists) {
          element.destroy();
          this.noteElements.delete(id);
        }
      }
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

    // Добавляем методы для обновления элементов при изменении в сторе
    updateCardElement(cardId, newCardData) {
      // Удаляем старый элемент
      const oldGroup = this.cardElements.get(cardId)
      if (oldGroup) {
        oldGroup.destroy()
        this.cardElements.delete(cardId)
      }
      // Создаем новый элемент
      this.renderCard(newCardData)
    },

    updateNoteElement(noteId, newNoteData) {
      // Удаляем старый элемент
      const oldGroup = this.noteElements.get(noteId)
      if (oldGroup) {
        oldGroup.destroy()
        this.noteElements.delete(noteId)
      }
      // Создаем новый элемент
      this.renderNote(newNoteData)
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
      try {
        await this.canvasStore.updateNote(noteId, { x, y })
      } catch (error) {
        console.error('Error updating note position:', error)
      }
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