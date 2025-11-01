<template>
  <div class="toolbar">
    <button @click="addCard" class="btn">➕ Задача</button>
    <button @click="addNote" class="btn">📝 Заметка</button>
    <button @click="toggleView" class="btn">{{ isGraphView ? 'Холст' : 'Граф' }}</button>
    <input v-model="searchQuery" @input="search" placeholder="Поиск..." class="search-input">
    <button @click="exportData" class="btn">📄 Экспорт</button>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';
import { useCanvasStore } from '../stores/canvas';

export default {
  name: 'Toolbar',
  data() {
    return {
      searchQuery: '',
      isGraphView: false
    }
  },
  setup() {
    const canvasStore = useCanvasStore()
    const router = useRouter()
    return { canvasStore, router }
  },
  methods: {
    async addCard() {
      const cardData = {
        title: 'Новая задача',
        x: Math.random() * 500,
        y: Math.random() * 500
      }
      // Вызываем событие для добавления карточки на холсте
      this.$emit('add-card', cardData)
    },

    async addNote() {
      const noteData = {
        title: 'Новая заметка',
        x: Math.random() * 500,
        y: Math.random() * 500
      }
      // Вызываем событие для добавления заметки на холсте
      this.$emit('add-note', noteData)
    },

    toggleView() {
      this.isGraphView = !this.isGraphView
      this.router.push(this.isGraphView ? '/graph' : '/')
    },

    search() {
      // TODO: Implement search
      console.log('Searching for:', this.searchQuery)
    },

    exportData() {
      // TODO: Implement export
      console.log('Exporting data...')
    }
  }
}
</script>

<style scoped>
.toolbar {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 1000;
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.btn:hover {
  background: #f5f5f5;
}

.search-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}
</style>