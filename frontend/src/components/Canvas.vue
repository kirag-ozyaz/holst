<template>
  <div class="canvas-container">
    <div ref="stageContainer" class="stage-container"></div>
  </div>
</template>

<script>
import Konva from 'konva';
import { markRaw, onMounted, onUnmounted, ref, toRaw } from 'vue';
import { NoteCard } from '../classes/NoteCard.js';
import { TaskCard } from '../classes/TaskCard.js';
import { CanvasElementService } from '../services/CanvasElementService.js';
import { useCanvasStore } from '../stores/canvas';

export default {
  name: 'Canvas',
  setup() {
    // Используем специальную функцию для создания безопасных объектов Konva
    // Создаем полностью изолированный контекст для работы с Konva
    const stage = ref(null);
    const layer = ref(null);
    const elementService = ref(null);
    // Используем обычные JS структуры данных вместо реактивных refs
    const elements = markRaw(new Map());
    const linkElements = markRaw([]);
    
    // Функция для безопасного создания объектов Konva
    const createSafeKonvaObject = (factoryFn) => {
      try {
        // Создаем объект с использованием markRaw для полной изоляции от реактивности Vue
        const obj = markRaw(factoryFn());
        return obj;
      } catch (error) {
        console.error('Error creating safe Konva object:', error);
        return null;
      }
    };
    
    const canvasStore = useCanvasStore();
    
    const initCanvas = () => {
      // Создаем сцену и слой с markRaw для полной изоляции
      const stageObj = markRaw(new Konva.Stage({
        container: document.querySelector('.stage-container'),
        width: window.innerWidth,
        height: window.innerHeight,
        draggable: true
      }));

      const layerObj = markRaw(new Konva.Layer());
      stageObj.add(layerObj);
      
      // Сохраняем объекты в refs
      stage.value = stageObj;
      layer.value = layerObj;

      // Клик по пустому месту - снять выделение
      stage.value.on('click', (e) => {
        if (e.target === stage.value) {
          canvasStore.setSelectedElement(null)
        }
      })

      // Zoom functionality
      stage.value.on('wheel', (e) => {
        e.evt.preventDefault()
        const scaleBy = 1.1
        const oldScale = stage.value.scaleX()
        const pointer = stage.value.getPointerPosition()

        const mousePointTo = {
          x: (pointer.x - stage.value.x()) / oldScale,
          y: (pointer.y - stage.value.y()) / oldScale,
        }

        const newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy
        stage.value.scale({ x: newScale, y: newScale })

        const newPos = {
          x: pointer.x - mousePointTo.x * newScale,
          y: pointer.y - mousePointTo.y * newScale,
        }
        stage.value.position(newPos)
        stage.value.batchDraw()
      })

      window.addEventListener('resize', handleResize)
    };
    
    const handleResize = () => {
      if (stage.value) {
        stage.value.width(window.innerWidth)
        stage.value.height(window.innerHeight)
      }
    };
    
    const loadData = async () => {
      await canvasStore.loadData()
      renderCanvas()
    };
    
    const renderCanvas = () => {
      // Сначала обновляем существующие элементы
      updateExistingElements();

      // Затем добавляем новые элементы
      addNewElements();

      // Удаляем удаленные элементы
      removeDeletedElements();

      // Рендерим связи (они должны быть под элементами)
      renderLinks();

      // Поддерживаем правильный порядок элементов
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
      // Добавляем новые карточки
      canvasStore.cards.forEach(card => {
        if (!elements.has(card.id)) {
          createElement(card, 'task');
        }
      });
      
      // Добавляем новые заметки
      canvasStore.notes.forEach(note => {
        if (!elements.has(note.id)) {
          createElement(note, 'note');
        }
      });
      
      // Восстанавливаем порядок по z_index
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
        const sourceElement = toRaw(elements.get(link.source_id))
        const targetElement = toRaw(elements.get(link.target_id))

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
      })
    };
    
    const updateCardPosition = async (cardId, x, y, zIndex) => {
      const updateData = { x, y };
      if (zIndex !== undefined) {
        updateData.z_index = zIndex;
      }
      await canvasStore.updateCard(cardId, updateData);
    };
    
    const updateNotePosition = async (noteId, x, y, zIndex) => {
      try {
        const updateData = { x, y };
        if (zIndex !== undefined) {
          updateData.z_index = zIndex;
        }
        await canvasStore.updateNote(noteId, updateData);
      } catch (error) {
        console.error('Error updating note position:', error)
      }
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
        await canvasStore.createCard(cardData)
      } catch (error) {
        console.error('Error adding card:', error)
      }
    };
    
    const addNote = async (noteData) => {
      try {
        if (noteData.x === undefined || noteData.y === undefined) {
          noteData.x = 150;
          noteData.y = 150;
        }
        await canvasStore.createNote(noteData)
      } catch (error) {
        console.error('Error adding note:', error)
      }
    };
    
    onMounted(() => {
      elementService.value = new CanvasElementService(canvasStore);
      initCanvas();
      loadData();
    });
    
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize);
    });
    
    return {
      canvasStore,
      stage,
      layer,
      elementService,
      elements,
      linkElements,
      initCanvas,
      addCard,
      addNote,
      handleResize,
      loadData,
      renderCanvas,
      updateExistingElements,
      addNewElements,
      removeDeletedElements,
      renderLinks,
      updateCardPosition,
      updateNotePosition,
      createElement,
      maintainElementsOrder
    };
  },
  mounted() {
    this.elementService = new CanvasElementService(this.canvasStore);
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

    // Watch for changes in selected element
    let previousSelectedElement = null;
    this.canvasStore.$subscribe((mutation, state) => {
      if (this.canvasStore.selectedElement !== previousSelectedElement) {
        // Снимаем выделение с предыдущего элемента
        if (previousSelectedElement) {
          const element = toRaw(this.elements.get(previousSelectedElement.id));
          if (element) {
            element.removeSelection();
          }
        }

        // Выделяем новый элемент, если он есть
        if (this.canvasStore.selectedElement) {
          const element = toRaw(this.elements.get(this.canvasStore.selectedElement.id));
          if (element) {
            element.setSelected();
          }
        }

        this.layer.draw();
        previousSelectedElement = this.canvasStore.selectedElement;
      }
    });
  },
  methods: {
    initCanvas() {
      this.stage = new Konva.Stage({
        container: this.$refs.stageContainer,
        width: window.innerWidth,
        height: window.innerHeight,
        draggable: true
      });

      this.layer = new Konva.Layer();
      this.stage.add(this.layer);

      // Клик по пустому месту - снять выделение
      this.stage.on('click', (e) => {
        if (e.target === this.stage) {
          this.canvasStore.setSelectedElement(null)
        }
      })

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

      window.addEventListener('resize', this.handleResize)
    },

    async addCard(cardData) {
      try {
        if (cardData.x === undefined || cardData.y === undefined) {
          cardData.x = 100;
          cardData.y = 100;
        }
        await this.canvasStore.createCard(cardData)
      } catch (error) {
        console.error('Error adding card:', error)
      }
    },

    async addNote(noteData) {
      try {
        if (noteData.x === undefined || noteData.y === undefined) {
          noteData.x = 150;
          noteData.y = 150;
        }
        await this.canvasStore.createNote(noteData)
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

      // Рендерим связи (они должны быть под элементами)
      this.renderLinks();

      // Поддерживаем правильный порядок элементов
      this.maintainElementsOrder();

      this.layer.draw();
    },
    
    updateExistingElements() {
      // Обновляем существующие карточки с использованием toRaw и markRaw
      this.canvasStore.cards.forEach(card => {
        const element = toRaw(this.elements.get(card.id));
        if (element) {
          markRaw(element).updatePosition(card.x, card.y);
        }
      });
      
      // Обновляем существующие заметки с использованием toRaw и markRaw
      this.canvasStore.notes.forEach(note => {
        const element = toRaw(this.elements.get(note.id));
        if (element) {
          markRaw(element).updatePosition(note.x, note.y);
        }
      });
    },
    
    addNewElements() {
      // Добавляем новые карточки с использованием toRaw и markRaw
      this.canvasStore.cards.forEach(card => {
        if (!toRaw(this.elements).has(card.id)) {
          this.createElement(card, 'card');
        }
      });
      
      // Добавляем новые заметки с использованием toRaw и markRaw
      this.canvasStore.notes.forEach(note => {
        if (!toRaw(this.elements).has(note.id)) {
          this.createElement(note, 'note');
        }
      });
      
      // Восстанавливаем порядок по z_index
      this.maintainElementsOrder();
    },
    
    removeDeletedElements() {
      // Удаляем удаленные элементы с использованием toRaw и markRaw
      for (let [id, element] of this.elements) {
        const cardExists = this.canvasStore.cards.some(card => card.id === id);
        const noteExists = this.canvasStore.notes.some(note => note.id === id);
        
        if (!cardExists && !noteExists) {
          const rawElement = toRaw(element);
          if (rawElement && typeof rawElement.destroy === 'function') {
            markRaw(rawElement).destroy();
          }
          this.elements.delete(id);
        }
      }
    },







    renderLinks() {
      // Очищаем существующие линии связей
      this.linkElements.forEach(link => {
        if (link && typeof link.destroy === 'function') {
          link.destroy();
        }
      });
      this.linkElements.length = 0;

      // Создаем новые линии связей с использованием markRaw
      this.canvasStore.taskLinks.forEach(link => {
        const sourceElement = toRaw(this.elements.get(link.source_id))
        const targetElement = toRaw(this.elements.get(link.target_id))

        if (sourceElement && targetElement && sourceElement.group && targetElement.group) {
          // Создаем линию
          const line = new Konva.Line({
            points: [
              sourceElement.group.x() + (sourceElement.group.children[0].width() / 2),
              sourceElement.group.y() + (sourceElement.group.children[0].height() / 2),
              targetElement.group.x() + (targetElement.group.children[0].width() / 2),
              targetElement.group.y() + (targetElement.group.children[0].height() / 2)
            ],
            stroke: 'gray',
            strokeWidth: 2,
            dash: [5, 5]
          });

          // Добавляем линию на слой
          this.layer.add(line);
          line.moveToBottom();
          // Добавляем линию в коллекцию
          this.linkElements.push(line);
        }
      })
    },

    async updateCardPosition(cardId, x, y, zIndex) {
      const updateData = { x, y };
      if (zIndex !== undefined) {
        updateData.z_index = zIndex;
      }
      await this.canvasStore.updateCard(cardId, updateData);
    },

    async updateNotePosition(noteId, x, y, zIndex) {
      try {
        const updateData = { x, y };
        if (zIndex !== undefined) {
          updateData.z_index = zIndex;
        }
        await this.canvasStore.updateNote(noteId, updateData);
      } catch (error) {
        console.error('Error updating note position:', error)
      }
    },



    /**
     * Создает новый элемент холста
     */
    createElement(data, type) {
      try {
        // Создаем элемент
        let element;
        
        if (type === 'card') {
          element = new TaskCard(data, this.elementService, this.layer);
        } else if (type === 'note') {
          element = new NoteCard(data, this.elementService, this.layer);
        }
        
        if (element) {
          // Устанавливаем родителя для элемента
          element.layer.parent = this;
          
          // Создаем группу
          const group = element.createGroup();
          if (group && group.children && group.children.length > 0) {
            // Добавляем группу на слой
            this.layer.add(group);
            // Сохраняем элемент в коллекции
            this.elements.set(data.id, element);
          }
        }
      } catch (error) {
        console.error('Error creating element:', error, data);
      }
    },

    /**
     * Поддерживает порядок активных элементов на переднем плане
     */


    /**
     * Поддерживает правильный порядок элементов по z_index
     */
    maintainElementsOrder() {
      // Получаем отсортированные элементы
      const sortedElements = this.elementService.getSortedElements();
      
      sortedElements.forEach(data => {
        // Получаем элемент
        const element = this.elements.get(data.id);
        if (element && element.group) {
          // Перемещаем группу на передний план
          element.group.moveToTop();
        }
      });
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