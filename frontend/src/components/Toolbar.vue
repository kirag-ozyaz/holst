<template>
  <div class="toolbar-wrap">
    <div v-if="errorMessage" class="error-banner" role="alert">
      {{ errorMessage }}
      <button type="button" class="error-dismiss" @click="errorMessage = ''">×</button>
    </div>
    <div class="toolbar">
      <button @click="addCard" class="btn" :disabled="creating">➕ Задача</button>
      <button @click="addNote" class="btn" :disabled="creating">📝 Заметка</button>
      <button
        @click="toggleLinkMode"
        class="btn"
        :class="{ active: canvasStore.linkMode }"
        :disabled="isGraphView"
        :title="isGraphView ? 'Связи создаются на холсте' : ''"
      >
        🔗 {{ canvasStore.linkMode ? 'Связь…' : 'Связь' }}
      </button>
      <button @click="toggleView" class="btn">{{ isGraphView ? 'Холст' : 'Граф' }}</button>
      <input v-model="searchQuery" @input="search" placeholder="Поиск..." class="search-input" disabled title="Фаза 2">
      <button @click="exportData" class="btn" disabled title="Фаза 3">📄 Экспорт</button>
    </div>
  </div>
</template>

<script>
import { useRoute, useRouter } from 'vue-router';
import { useCanvasStore } from '../stores/canvas';

export default {
  name: 'Toolbar',
  data() {
    return {
      searchQuery: '',
      creating: false,
      errorMessage: ''
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
    showError(message) {
      this.errorMessage = message
      window.clearTimeout(this._errorTimer)
      this._errorTimer = window.setTimeout(() => {
        this.errorMessage = ''
      }, 8000)
    },

    apiErrorMessage(error) {
      const detail = error?.response?.data?.detail
      if (typeof detail === 'string') return detail
      if (Array.isArray(detail)) return detail.map(d => d.msg || JSON.stringify(d)).join('; ')
      if (error?.response?.status === 404) return 'API не найден (проверьте прокси /api и backend)'
      if (error?.message === 'Network Error') return 'Нет связи с сервером (backend или CORS)'
      return error?.message || 'Не удалось выполнить запрос'
    },

    randomPosition() {
      return {
        x: Math.round(100 + Math.random() * 400),
        y: Math.round(100 + Math.random() * 400)
      }
    },

    async addCard() {
      await this.createOnCanvas('task')
    },

    async addNote() {
      await this.createOnCanvas('note')
    },

    async createOnCanvas(kind) {
      if (this.creating) return
      this.creating = true
      this.errorMessage = ''

      const payload = {
        title: kind === 'task' ? 'Новая задача' : 'Новая заметка',
        content: [],
        ...this.randomPosition()
      }

      try {
        if (kind === 'task') {
          await this.canvasStore.createCard(payload)
        } else {
          await this.canvasStore.createNote(payload)
        }

        if (this.isGraphView) {
          await this.router.push('/')
        }
      } catch (error) {
        console.error(`Error creating ${kind}:`, error)
        this.showError(this.apiErrorMessage(error))
      } finally {
        this.creating = false
      }
    },

    toggleLinkMode() {
      if (this.isGraphView) return
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
.toolbar-wrap {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: calc(100vw - 20px);
}

.error-banner {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 8px 36px 8px 12px;
  font-size: 13px;
  position: relative;
  max-width: 520px;
}

.error-dismiss {
  position: absolute;
  right: 8px;
  top: 4px;
  border: none;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
  color: #991b1b;
}

.toolbar {
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
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
