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

      <div v-if="relatedLinks.length" class="form-group">
        <label>Связи</label>
        <ul class="links-list">
          <li v-for="link in relatedLinks" :key="`${link.kind}-${link.id}`">
            <span class="link-label">{{ linkLabel(link) }}</span>
            <button type="button" class="btn-link-delete" @click="removeLink(link)">×</button>
          </li>
        </ul>
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
import { ref, watch, computed } from 'vue';
import { useCanvasStore } from '../stores/canvas';

const canvasStore = useCanvasStore();

const props = defineProps({
  element: {
    type: Object,
    default: null
  }
});

const form = ref({
  title: '',
  content: ''
});

const relatedLinks = computed(() => {
  if (!props.element) return [];
  return canvasStore.linksForElement(props.element.id);
});

watch(() => props.element, (newElement) => {
  if (newElement) {
    form.value.title = newElement.title || '';
    form.value.content = formatContentForEdit(newElement.content);
  }
}, { immediate: true });

function formatContentForEdit(content) {
  if (content == null) return '';
  if (Array.isArray(content)) {
    return content.length ? JSON.stringify(content, null, 2) : '';
  }
  if (typeof content === 'object') {
    return JSON.stringify(content, null, 2);
  }
  return String(content);
}

function parseContentForSave(raw) {
  const trimmed = raw.trim();
  if (!trimmed) return [];
  if (trimmed.startsWith('[') || trimmed.startsWith('{')) {
    try {
      return JSON.parse(trimmed);
    } catch {
      return trimmed;
    }
  }
  return trimmed;
}

const saveChanges = async () => {
  if (!props.element) return;

  try {
    const updateData = {
      title: form.value.title,
      content: parseContentForSave(form.value.content)
    };

    if (props.element.type === 'task') {
      await canvasStore.updateCard(props.element.id, updateData);
    } else if (props.element.type === 'note') {
      await canvasStore.updateNote(props.element.id, updateData);
    }
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
      await canvasStore.deleteNote(props.element.id);
    }
  } catch (error) {
    console.error('Error deleting element:', error);
    alert('Ошибка при удалении');
  }
};

function linkLabel(link) {
  const otherId = link.source_id === props.element.id ? link.target_id : link.source_id;
  const card = canvasStore.cards.find(c => c.id === otherId);
  if (card) return `→ ${card.title || 'Задача'}`;
  const note = canvasStore.notes.find(n => n.id === otherId);
  if (note) return `→ ${note.title || 'Заметка'}`;
  return `→ ${otherId}`;
}

async function removeLink(link) {
  try {
    if (link.kind === 'task') {
      await canvasStore.deleteTaskLink(link.id);
    } else {
      await canvasStore.deleteNoteLink(link.id);
    }
  } catch (error) {
    alert('Не удалось удалить связь');
  }
}

const closeEditor = () => {
  canvasStore.setSelectedElement(null);
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
  box-sizing: border-box;
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.links-list {
  list-style: none;
  margin: 0;
  padding: 0;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  max-height: 120px;
  overflow-y: auto;
}

.links-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  border-bottom: 1px solid #f3f4f6;
  font-size: 13px;
}

.links-list li:last-child {
  border-bottom: none;
}

.btn-link-delete {
  border: none;
  background: #fee2e2;
  color: #b91c1c;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
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
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-danger {
  background: #ef4444;
  color: white;
}
</style>
