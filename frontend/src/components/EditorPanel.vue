<template>
  <div class="editor-panel">
    <div class="editor-header">
      <h3 class="editor-title">
        {{ element ? (element.type === 'task' ? 'Редактирование задачи' : 'Редактирование заметки') : '' }}
      </h3>
      <button class="close-button" @click="closeEditor">
        &times;
      </button>
    </div>

    <div v-if="element" class="editor-content">
      <div class="form-group">
        <label for="title">Заголовок</label>
        <input
          id="title"
          type="text"
          v-model="form.title"
          placeholder="Введите заголовок..."
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label for="content">Содержимое</label>
        <textarea
          id="content"
          v-model="form.content"
          placeholder="Введите содержимое..."
          class="form-input form-textarea"
          rows="8"
        ></textarea>
      </div>

      <div class="form-actions">
        <button class="btn btn-primary" @click="saveChanges">
          Сохранить
        </button>
        <button class="btn btn-danger" @click="deleteElement">
          Удалить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, toRaw } from 'vue';
import { useCanvasStore } from '../stores/canvas';

const canvasStore = useCanvasStore();

const props = defineProps({
  element: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close']);

const form = ref({
  title: '',
  content: ''
});

watch(() => props.element, (newElement) => {
  if (newElement) {
    form.value.title = newElement.title || '';
    form.value.content = Array.isArray(newElement.content) ? JSON.stringify(newElement.content, null, 2) : (newElement.content || '');
  }
}, { immediate: true });

const saveChanges = async () => {
  if (!props.element) return;

  try {
    const updateData = {
      title: form.value.title,
      content: form.value.content
    };

    if (props.element.type === 'task') {
      await canvasStore.updateCard(props.element.id, updateData);
    } else if (props.element.type === 'note') {
      await canvasStore.updateNote(props.element.id, updateData);
    }

    closeEditor();
  } catch (error) {
    console.error('Error saving element:', error);
    alert('Ошибка при сохранении');
  }
};

const deleteElement = async () => {
  if (!props.element) return;

  if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
    return;
  }

  try {
    if (props.element.type === 'task') {
      await canvasStore.deleteCard(props.element.id);
    } else if (props.element.type === 'note') {
      await canvasStore.updateNote(props.element.id, { deleted: true });
    }

    closeEditor();
  } catch (error) {
    console.error('Error deleting element:', error);
    alert('Ошибка при удалении');
  }
};

const closeEditor = () => {
  canvasStore.setSelectedElement(null);
  emit('close');
};
</script>

<style scoped>
.editor-panel {
  position: absolute;
  top: 60px;
  right: 20px;
  width: 400px;
  max-height: calc(100vh - 80px);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.editor-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}

.close-button:hover {
  color: #1f2937;
}

.editor-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}
</style>
