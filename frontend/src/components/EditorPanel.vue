<template>
  <div class="editor-panel" :style="panelStyle">
    <div
      class="editor-header"
      :class="{ 'editor-header-draggable': true }"
      @mousedown="onHeaderPointerDown"
    >
      <h3 class="editor-title">
        {{ element ? (element.type === 'task' ? 'Редактирование задачи' : 'Редактирование заметки') : '' }}
      </h3>
      <button class="close-button" @click="closeEditor">
        &times;
      </button>
    </div>

    <div v-if="element" class="editor-content">
      <p v-if="elementMeta" class="editor-meta">{{ elementMeta }}</p>
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

      <div v-if="element.type === 'task'" class="form-group">
        <label>Привязать заметку</label>
        <div class="attach-row">
          <select v-model="selectedNoteToAttach" class="form-input form-select">
            <option value="">— выберите заметку —</option>
            <option v-for="note in availableNotes" :key="note.id" :value="note.id">
              {{ formatCardListLine('note', note) }}
            </option>
          </select>
          <button
            type="button"
            class="btn btn-secondary btn-sm"
            :disabled="!selectedNoteToAttach"
            @click="attachSelectedNote"
          >
            Привязать
          </button>
        </div>
        <button type="button" class="btn btn-secondary btn-block" @click="createAndAttachNote">
          + Создать новую заметку
        </button>
      </div>

      <div v-if="element.type === 'note'" class="form-group">
        <label for="parent-task">Задача (привязка)</label>
        <select
          id="parent-task"
          v-model="parentTaskId"
          class="form-input form-select"
          @change="onParentTaskChange"
        >
          <option value="">— без задачи —</option>
          <option v-for="task in canvasStore.cards" :key="task.id" :value="task.id">
            {{ formatCardListLine('task', task) }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>Связи</label>
        <p v-if="!allRelatedLinks.length" class="hint-text">
          Нет связей — режим «Связь» на холсте или привязка заметки к задаче
        </p>
        <ul v-else class="links-list links-list-interactive">
          <li
            v-for="link in allRelatedLinks"
            :key="`${link.kind}-${link.id}`"
            :class="{ 'link-row-active': isLinkHighlighted(link) }"
            @click="selectLink(link)"
          >
            <span class="link-label">{{ linkRowLabel(link) }}</span>
            <div class="link-row-actions" @click.stop>
              <button
                v-if="canDetachTaskNote(link)"
                type="button"
                class="btn-link-action btn-link-detach"
                title="Отвязать заметку"
                @click="detachTaskNoteLink(link)"
              >
                Отвязать
              </button>
              <button
                type="button"
                class="btn-link-delete"
                title="Удалить связь"
                @click="removeLink(link)"
              >
                ×
              </button>
            </div>
          </li>
        </ul>
        <p v-if="allRelatedLinks.length" class="hint-text hint-text-sm">
          Нажмите на связь, чтобы подсветить стрелку на холсте
        </p>
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
import { ref, watch, computed, onUnmounted } from 'vue';
import { useCanvasStore } from '../stores/canvas';
import { formatCardListLine, formatCardMetaLine } from '../utils/cardDisplay.js';

const canvasStore = useCanvasStore();

const PANEL_WIDTH = 360;

const panelStyle = computed(() => {
  const userPos = canvasStore.editorPanelPosition;
  if (userPos) {
    return {
      left: `${userPos.left}px`,
      top: `${userPos.top}px`,
      width: `${PANEL_WIDTH}px`
    };
  }
  const anchor = canvasStore.editorAnchor;
  if (anchor) {
    return {
      left: `${anchor.left}px`,
      top: `${anchor.top}px`,
      width: `${PANEL_WIDTH}px`
    };
  }
  return {
    top: '60px',
    right: '20px',
    width: `${PANEL_WIDTH}px`
  };
});

let dragState = null;

function onHeaderPointerDown(event) {
  if (event.button !== 0) {
    return;
  }
  if (event.target.closest('.close-button')) {
    return;
  }
  event.preventDefault();
  const panel = event.currentTarget.closest('.editor-panel');
  if (!panel) {
    return;
  }
  const rect = panel.getBoundingClientRect();
  dragState = {
    startX: event.clientX,
    startY: event.clientY,
    originLeft: rect.left,
    originTop: rect.top
  };
  window.addEventListener('mousemove', onHeaderPointerMove);
  window.addEventListener('mouseup', onHeaderPointerUp);
}

function onHeaderPointerMove(event) {
  if (!dragState) {
    return;
  }
  const dx = event.clientX - dragState.startX;
  const dy = event.clientY - dragState.startY;
  const left = Math.max(
    8,
    Math.min(dragState.originLeft + dx, window.innerWidth - PANEL_WIDTH - 8)
  );
  const top = Math.max(56, Math.min(dragState.originTop + dy, window.innerHeight - 80));
  canvasStore.setEditorPanelPosition({ left, top });
}

function onHeaderPointerUp() {
  dragState = null;
  window.removeEventListener('mousemove', onHeaderPointerMove);
  window.removeEventListener('mouseup', onHeaderPointerUp);
}

onUnmounted(() => {
  window.removeEventListener('mousemove', onHeaderPointerMove);
  window.removeEventListener('mouseup', onHeaderPointerUp);
});

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

const selectedNoteToAttach = ref('');
const parentTaskId = ref('');

const availableNotes = computed(() => {
  if (!props.element || props.element.type !== 'task') return [];
  return canvasStore.notesAvailableToAttach(props.element.id);
});

const allRelatedLinks = computed(() => {
  if (!props.element) return [];
  return canvasStore.linksForElement(props.element.id);
});

const elementMeta = computed(() => {
  if (!props.element?.type) return '';
  return formatCardMetaLine(props.element.type, props.element);
});

watch(() => props.element, (newElement) => {
  if (newElement) {
    form.value.title = newElement.title || '';
    form.value.content = formatContentForEdit(newElement.content);
    selectedNoteToAttach.value = '';
    parentTaskId.value =
      newElement.type === 'note' && newElement.task_id ? newElement.task_id : '';
  }
}, { immediate: true });

watch(
  () => canvasStore.notes.map(n => `${n.id}:${n.task_id}:${n.title}`).join('|'),
  () => {
    if (props.element?.type === 'note') {
      const fresh = canvasStore.notes.find(n => n.id === props.element.id);
      if (fresh) {
        parentTaskId.value = fresh.task_id || '';
      }
    }
  }
);

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

function endpointEntityType(link, role) {
  if (link.kind === 'note') {
    return 'note';
  }
  if (role === 'source') {
    return 'task';
  }
  if (link.link_target_type === 'note' || link.link_target_type === 'card') {
    return 'note';
  }
  return 'task';
}

function formatLinkEndpoint(id, link, role) {
  const entityType = endpointEntityType(link, role);
  if (entityType === 'task') {
    const card = canvasStore.cards.find(c => c.id === id);
    return formatCardListLine('task', card || { title: 'Задача' });
  }
  const note = canvasStore.notes.find(n => n.id === id);
  return formatCardListLine('note', note || { title: 'Заметка' });
}

function linkTypeHint(link) {
  if (link.kind === 'note') return 'заметка↔заметка';
  if (link.link_target_type === 'note' || link.link_target_type === 'card') {
    return 'задача→заметка';
  }
  return 'задача→задача';
}

function linkRowLabel(link) {
  const from = formatLinkEndpoint(link.source_id, link, 'source');
  const to = formatLinkEndpoint(link.target_id, link, 'target');
  return `${from} → ${to} (${linkTypeHint(link)})`;
}

function isLinkHighlighted(link) {
  return canvasStore.highlightedLinkKey === canvasStore.linkKey(link.kind, link.id);
}

function selectLink(link) {
  canvasStore.setHighlightedLink(link.kind, link.id);
}

function isTaskNoteLink(link) {
  return (
    link.kind === 'task' &&
    (link.link_target_type === 'note' || link.link_target_type === 'card')
  );
}

function canDetachTaskNote(link) {
  if (!isTaskNoteLink(link) || !props.element) return false;
  if (props.element.type === 'task' && link.source_id === props.element.id) return true;
  if (props.element.type === 'note' && link.target_id === props.element.id) return true;
  return false;
}

async function detachTaskNoteLink(link) {
  if (!canDetachTaskNote(link)) return;
  try {
    await canvasStore.detachNoteFromTask(link.source_id, link.target_id);
  } catch (error) {
    console.error(error);
    alert('Не удалось отвязать заметку');
  }
}

async function attachSelectedNote() {
  if (!props.element || !selectedNoteToAttach.value) return;
  try {
    await canvasStore.attachNoteToTask(props.element.id, selectedNoteToAttach.value);
    selectedNoteToAttach.value = '';
  } catch (error) {
    console.error(error);
    alert('Не удалось привязать заметку');
  }
}

async function createAndAttachNote() {
  if (!props.element) return;
  try {
    await canvasStore.createNoteForTask(props.element.id);
  } catch (error) {
    console.error(error);
    alert('Не удалось создать заметку');
  }
}

async function onParentTaskChange() {
  if (!props.element || props.element.type !== 'note') return;
  try {
    await canvasStore.setNoteParentTask(
      props.element.id,
      parentTaskId.value || null
    );
  } catch (error) {
    console.error(error);
    alert('Не удалось изменить привязку к задаче');
  }
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
  canvasStore.closeEditor();
};
</script>

<style scoped>
.editor-panel {
  position: fixed;
  max-height: calc(100vh - 80px);
  background: var(--holst-bg-surface);
  color: var(--holst-text);
  border-radius: 8px;
  box-shadow: var(--holst-shadow-md);
  border: 1px solid var(--holst-border);
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--holst-border);
}

.editor-header-draggable {
  cursor: grab;
  user-select: none;
}

.editor-header-draggable:active {
  cursor: grabbing;
}

.editor-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--holst-text);
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--holst-text-muted);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-button:hover {
  color: var(--holst-text);
}

.editor-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.editor-meta {
  margin: 0 0 14px;
  font-size: 12px;
  font-weight: 600;
  color: var(--holst-text-muted);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--holst-text);
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--holst-border-strong);
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  box-sizing: border-box;
  background: var(--holst-bg-surface);
  color: var(--holst-text);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.links-list {
  list-style: none;
  margin: 0;
  padding: 0;
  border: 1px solid var(--holst-border);
  border-radius: 6px;
  max-height: 200px;
  overflow-y: auto;
}

.links-list-interactive li {
  cursor: pointer;
  transition: background 0.15s ease;
}

.links-list-interactive li:hover {
  background: var(--holst-bg-muted);
}

.links-list li.link-row-active {
  background: var(--holst-accent-soft);
  box-shadow: inset 3px 0 0 var(--holst-accent);
}

.links-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  border-bottom: 1px solid var(--holst-border);
  font-size: 13px;
  gap: 8px;
}

.link-row-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.links-list li:last-child {
  border-bottom: none;
}

.btn-link-delete {
  border: none;
  background: var(--holst-danger-bg);
  color: var(--holst-danger-text);
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
  background: var(--holst-accent);
  color: #ffffff;
}

.btn-secondary {
  background: var(--holst-bg-muted);
  color: var(--holst-text);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--holst-border-strong);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 8px 12px;
  font-size: 13px;
  white-space: nowrap;
}

.btn-block {
  width: 100%;
  margin-top: 8px;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.form-select {
  cursor: pointer;
}

.attach-row {
  display: flex;
  gap: 8px;
  align-items: stretch;
  margin-top: 8px;
}

.attach-row .form-select {
  flex: 1;
  min-width: 0;
}

.hint-text {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--holst-text-muted);
}

.hint-text-sm {
  margin: 6px 0 0;
  font-size: 12px;
}

.btn-link-action {
  border: none;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-link-detach {
  background: var(--holst-warn-bg);
  color: var(--holst-warn-text);
}
</style>
