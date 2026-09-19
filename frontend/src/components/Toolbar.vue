<template>
  <div class="toolbar">
    <button @click="addCard" class="btn">➕ Задача</button>
    <button @click="addNote" class="btn">📝 Заметка</button>
    <button
      @click="toggleLinkMode"
      class="btn"
      :class="{ active: canvasStore.linkMode }"
    >
      🔗 {{ canvasStore.linkMode ? 'Связь…' : 'Связь' }}
    </button>
    <button @click="toggleView" class="btn">{{ isGraphView ? 'Холст' : 'Граф' }}</button>
    <input v-model="searchQuery" @input="search" placeholder="Поиск..." class="search-input" disabled title="Фаза 2">
    <button @click="exportData" class="btn" disabled title="Фаза 3">📄 Экспорт</button>
  </div>
</template>

<script>
import { useRoute, useRouter } from 'vue-router';
import { useCanvasStore } from '../stores/canvas';

export default {
  name: 'Toolbar',
  emits: ['add-card', 'add-note'],
  data() {
    return {
      searchQuery: ''
    }
  },
  setup() {
    const canvasStore = useCanvasStore()
    const router = useRouter()
    const route = useRoute()
    return { canvasStore, router, route }
  },
  computed: {
    isGraphView() {
      return this.route.path === '/graph'
    }
  },
  methods: {
    addCard() {
      this.$emit('add-card', {
        title: 'Новая задача',
        x: Math.random() * 500,
        y: Math.random() * 500
      })
    },

    addNote() {
      this.$emit('add-note', {
        title: 'Новая заметка',
        x: Math.random() * 500,
        y: Math.random() * 500
      })
    },

    toggleLinkMode() {
      this.canvasStore.toggleLinkMode()
    },

    toggleView() {
      this.router.push(this.isGraphView ? '/' : '/graph')
    },

    search() {
      console.log('Searching for:', this.searchQuery)
    },

    exportData() {
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
  flex-wrap: wrap;
  max-width: calc(100vw - 20px);
}

.btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.btn.active {
  background: #dbeafe;
  border-color: #3b82f6;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}
</style>
