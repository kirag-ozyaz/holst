<template>
  <aside
    class="task-journal"
    aria-label="Журнал задач"
    :style="{ width: `${journalWidth}px` }"
  >
    <div class="journal-header">
      <div class="journal-title-block">
        <h2 class="journal-title">Журнал задач</h2>
        <span class="journal-count" aria-live="polite">{{ elementCountLabel }}</span>
      </div>
      <div class="journal-header-actions">
        <div class="journal-view-toggle" role="group" aria-label="Режим отображения">
          <button
            type="button"
            class="journal-view-btn"
            :class="{ 'journal-view-btn-active': viewMode === 'tree' }"
            title="Дерево"
            @click.stop="setViewMode('tree')"
          >
            Дерево
          </button>
          <button
            type="button"
            class="journal-view-btn"
            :class="{ 'journal-view-btn-active': viewMode === 'list' }"
            title="Список"
            @click.stop="setViewMode('list')"
          >
            Список
          </button>
        </div>
        <button type="button" class="journal-toggle" @click="collapsed = !collapsed">
          {{ collapsed ? '▸' : '▾' }}
        </button>
      </div>
    </div>

    <div v-show="!collapsed" class="journal-body">
      <p v-if="!visibleRows.length" class="journal-empty">Нет задач</p>
      <ul v-else class="journal-list">
        <li
          v-for="row in visibleRows"
          :key="row.key"
          class="journal-row"
          :class="{
            'journal-row-selected': isSelected(row),
            'journal-row-has-children': row.hasChildren && viewMode === 'tree',
            'journal-row-note': row.kind === 'note'
          }"
          :style="rowStyle(row)"
          @contextmenu.prevent="onRowContextMenu($event, row)"
        >
          <button
            v-if="viewMode === 'tree' && row.hasChildren"
            type="button"
            class="journal-expand"
            :aria-expanded="row.expanded"
            :title="row.expanded ? 'Свернуть' : 'Развернуть'"
            @click.stop="toggleExpand(row.key)"
          >
            {{ row.expanded ? '➖' : '➕' }}
          </button>
          <span
            v-else-if="viewMode === 'tree'"
            class="journal-expand journal-expand-placeholder"
            aria-hidden="true"
          />

          <button
            type="button"
            class="journal-label"
            @click="onRowSelect(row)"
          >
            <span v-if="row.kind === 'note'" class="journal-kind" aria-hidden="true">📝</span>
            <span class="journal-label-text">{{ rowLine(row) }}</span>
          </button>
        </li>
      </ul>
    </div>
    <div
      class="journal-resize-handle"
      role="separator"
      aria-orientation="vertical"
      aria-label="Изменить ширину журнала"
      @mousedown.prevent="startResize"
    />
  </aside>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue';
import { useCanvasStore } from '../stores/canvas';
import { formatCardListLine } from '../utils/cardDisplay.js';

const JOURNAL_VIEW_KEY = 'holst.journal.viewMode';
const JOURNAL_WIDTH_KEY = 'holst.journal.width';
const JOURNAL_WIDTH_MIN = 220;
const JOURNAL_WIDTH_MAX = 560;
const JOURNAL_WIDTH_DEFAULT = 300;

function readStoredJournalWidth() {
  if (typeof localStorage === 'undefined') {
    return JOURNAL_WIDTH_DEFAULT;
  }
  const raw = Number.parseInt(localStorage.getItem(JOURNAL_WIDTH_KEY) || '', 10);
  if (!Number.isFinite(raw)) {
    return JOURNAL_WIDTH_DEFAULT;
  }
  return Math.min(JOURNAL_WIDTH_MAX, Math.max(JOURNAL_WIDTH_MIN, raw));
}

const canvasStore = useCanvasStore();
const collapsed = ref(false);
const expandedKeys = ref(new Set());
const viewMode = ref(
  typeof localStorage !== 'undefined' && localStorage.getItem(JOURNAL_VIEW_KEY) === 'list'
    ? 'list'
    : 'tree'
);
const journalWidth = ref(readStoredJournalWidth());
const resizing = ref(false);

function persistJournalWidth(width) {
  try {
    localStorage.setItem(JOURNAL_WIDTH_KEY, String(width));
  } catch {
    /* ignore */
  }
}

function startResize(event) {
  resizing.value = true;
  const startX = event.clientX;
  const startWidth = journalWidth.value;

  const onMove = (moveEvent) => {
    const next = Math.min(
      JOURNAL_WIDTH_MAX,
      Math.max(JOURNAL_WIDTH_MIN, startWidth + (moveEvent.clientX - startX))
    );
    journalWidth.value = next;
  };

  const onUp = () => {
    resizing.value = false;
    persistJournalWidth(journalWidth.value);
    window.removeEventListener('mousemove', onMove);
    window.removeEventListener('mouseup', onUp);
  };

  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
}

onUnmounted(() => {
  if (resizing.value) {
    persistJournalWidth(journalWidth.value);
  }
});

function setViewMode(mode) {
  viewMode.value = mode;
  try {
    localStorage.setItem(JOURNAL_VIEW_KEY, mode);
  } catch {
    /* ignore */
  }
}

function rowLine(row) {
  if (row.kind === 'note') {
    const note = canvasStore.notes.find(n => n.id === row.id);
    return formatCardListLine('note', note || { title: row.title });
  }
  const task = canvasStore.cards.find(c => c.id === row.id);
  return formatCardListLine('task', task || { title: row.title });
}

function sortByTitle(items, getTitle) {
  return [...items].sort((a, b) =>
    (getTitle(a) || '').localeCompare(getTitle(b) || '', 'ru', { sensitivity: 'base' })
  );
}

function normalizeParentId(parentId) {
  return parentId || null;
}

/** Task that owns this note (task_id or task→note link); null = top-level in tree. */
function noteParentTaskId(note) {
  if (note.task_id && canvasStore.cards.some((c) => c.id === note.task_id)) {
    return note.task_id;
  }
  const link = canvasStore.taskLinks.find(
    (l) =>
      l.target_id === note.id &&
      (l.link_target_type === 'note' || l.link_target_type === 'card') &&
      canvasStore.cards.some((c) => c.id === l.source_id)
  );
  return link?.source_id ?? null;
}

const childrenByParent = computed(() => {
  const map = new Map();
  canvasStore.cards.forEach(task => {
    const key = normalizeParentId(task.parent_id);
    if (!map.has(key)) {
      map.set(key, []);
    }
    map.get(key).push(task);
  });
  map.forEach((list, key) => {
    map.set(key, sortByTitle(list, (t) => t.title));
  });
  return map;
});

/** Root tasks only: no parent_id, or parent missing (orphan). */
const rootTasks = computed(() => {
  const ids = new Set(canvasStore.cards.map(c => c.id));
  const roots = canvasStore.cards.filter(task => {
    const parentId = normalizeParentId(task.parent_id);
    if (!parentId) return true;
    return !ids.has(parentId);
  });
  return sortByTitle(roots, (t) => t.title);
});

/** Standalone notes: no task_id (and not link-attached to a task). */
const rootNotes = computed(() => {
  const roots = canvasStore.notes.filter((note) => noteParentTaskId(note) === null);
  return sortByTitle(roots, (n) => n.title);
});

function childTasks(taskId) {
  return childrenByParent.value.get(taskId) || [];
}

/** Notes subordinate to a task (task_id and/or task→note links). */
function childNotesOfTask(taskId) {
  return sortByTitle(canvasStore.notesAttachedToTask(taskId), (n) => n.title);
}

function hasTaskChildren(taskId) {
  return childTasks(taskId).length > 0 || childNotesOfTask(taskId).length > 0;
}

function pushTaskRows(task, depth, out) {
  const key = `task:${task.id}`;
  const expanded = expandedKeys.value.has(key);
  const hasChildren = hasTaskChildren(task.id);
  out.push({
    key,
    kind: 'task',
    id: task.id,
    title: task.title,
    depth,
    hasChildren,
    expanded
  });
  if (!hasChildren || !expanded) {
    return;
  }
  for (const child of childTasks(task.id)) {
    pushTaskRows(child, depth + 1, out);
  }
  for (const note of childNotesOfTask(task.id)) {
    pushNoteRow(note, depth + 1, out);
  }
}

function pushNoteRow(note, depth, out) {
  out.push({
    key: `note:${note.id}`,
    kind: 'note',
    id: note.id,
    title: note.title,
    depth,
    hasChildren: false,
    expanded: false
  });
}

const treeRows = computed(() => {
  const rows = [];
  const roots = [
    ...rootTasks.value.map((task) => ({
      kind: 'task',
      task,
      title: task.title || ''
    })),
    ...rootNotes.value.map((note) => ({
      kind: 'note',
      note,
      title: note.title || ''
    }))
  ].sort((a, b) =>
    a.title.localeCompare(b.title, 'ru', { sensitivity: 'base' })
  );

  for (const entry of roots) {
    if (entry.kind === 'task') {
      pushTaskRows(entry.task, 0, rows);
    } else {
      pushNoteRow(entry.note, 0, rows);
    }
  }
  return rows;
});

const listRows = computed(() => {
  const rows = [];
  for (const task of sortByTitle(canvasStore.cards, (t) => t.title)) {
    rows.push({
      key: `task:${task.id}`,
      kind: 'task',
      id: task.id,
      title: task.title,
      depth: 0,
      hasChildren: false,
      expanded: false
    });
  }
  for (const note of sortByTitle(canvasStore.notes, (n) => n.title)) {
    rows.push({
      key: `note:${note.id}`,
      kind: 'note',
      id: note.id,
      title: note.title,
      depth: 0,
      hasChildren: false,
      expanded: false
    });
  }
  return rows.sort((a, b) =>
    (a.title || '').localeCompare(b.title || '', 'ru', { sensitivity: 'base' })
  );
});

const visibleRows = computed(() => (viewMode.value === 'list' ? listRows.value : treeRows.value));

const elementCountLabel = computed(() => {
  const n = visibleRows.value.length;
  const word =
    n % 10 === 1 && n % 100 !== 11
      ? 'элемент'
      : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)
        ? 'элемента'
        : 'элементов';
  return `${n} ${word}`;
});

function rowStyle(row) {
  if (viewMode.value === 'list') {
    return { paddingLeft: '12px' };
  }
  return { paddingLeft: `${12 + row.depth * 16}px` };
}

function toggleExpand(key) {
  const next = new Set(expandedKeys.value);
  if (next.has(key)) {
    next.delete(key);
  } else {
    next.add(key);
  }
  expandedKeys.value = next;
}

function elementPayload(row) {
  if (row.kind === 'task') {
    const card = canvasStore.cards.find(c => c.id === row.id);
    return card ? { ...card, type: 'task' } : null;
  }
  const note = canvasStore.notes.find(n => n.id === row.id);
  return note ? { ...note, type: 'note' } : null;
}

function onRowSelect(row) {
  const el = elementPayload(row);
  if (el) {
    canvasStore.setSelectedElement(el);
  }
  if (viewMode.value === 'tree' && row.hasChildren) {
    toggleExpand(row.key);
  }
}

function onRowContextMenu(event, row) {
  if (canvasStore.linkMode) {
    return;
  }
  const el = elementPayload(row);
  if (!el) {
    return;
  }
  const previousSelection = canvasStore.selectedElement;
  canvasStore.setSelectedElement(el);
  canvasStore.openContextMenu(event.clientX, event.clientY, el, previousSelection);
}

function isSelected(row) {
  return (
    canvasStore.selectedElement?.type === row.kind &&
    canvasStore.selectedElement?.id === row.id
  );
}

watch(
  () =>
    [
      canvasStore.cards.map(c => `${c.id}:${c.parent_id}`).join(','),
      canvasStore.notes.map(n => `${n.id}:${n.task_id || ''}`).join(','),
      canvasStore.taskLinks.map(l => `${l.id}:${l.source_id}:${l.target_id}`).join(',')
    ].join('|'),
  () => {
    const valid = new Set();
    canvasStore.cards.forEach(c => valid.add(`task:${c.id}`));
    canvasStore.notes.forEach(n => valid.add(`note:${n.id}`));
    const next = new Set();
    expandedKeys.value.forEach(key => {
      if (valid.has(key)) {
        next.add(key);
      }
    });
    expandedKeys.value = next;
  }
);
</script>

<style scoped>
.task-journal {
  position: absolute;
  top: 70px;
  left: 10px;
  max-height: calc(100vh - 90px);
  background: var(--holst-bg-surface);
  color: var(--holst-text);
  border-radius: 8px;
  box-shadow: var(--holst-shadow-md);
  border: 1px solid var(--holst-border);
  z-index: 1001;
  pointer-events: auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.journal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--holst-border);
}

.journal-header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.journal-view-toggle {
  display: flex;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--holst-border);
}

.journal-view-btn {
  border: none;
  background: var(--holst-bg-muted);
  color: var(--holst-text-muted);
  font-size: 11px;
  padding: 4px 8px;
  cursor: pointer;
  line-height: 1.2;
}

.journal-view-btn-active {
  background: var(--holst-accent-soft);
  color: var(--holst-text);
  font-weight: 600;
}

.journal-title-block {
  min-width: 0;
  flex: 1;
}

.journal-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--holst-text);
  min-width: 0;
}

.journal-count {
  display: block;
  margin-top: 2px;
  font-size: 11px;
  font-weight: 500;
  color: var(--holst-text-muted);
}

.journal-toggle {
  border: none;
  background: var(--holst-bg-muted);
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--holst-text);
}

.journal-body {
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.journal-empty {
  margin: 0;
  padding: 14px;
  font-size: 13px;
  color: var(--holst-text-muted);
}

.journal-list {
  list-style: none;
  margin: 0;
  padding: 6px 0;
}

.journal-row {
  display: flex;
  align-items: center;
  gap: 4px;
  min-height: 34px;
  padding-right: 8px;
}

.journal-row-selected {
  background: var(--holst-accent-soft);
}

.journal-row-has-children .journal-label {
  font-weight: 600;
}

.journal-row-note .journal-label {
  font-weight: 400;
}

.journal-expand {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--holst-text);
  font-size: 14px;
  line-height: 1;
  border-radius: 4px;
}

.journal-expand:hover {
  background: var(--holst-bg-muted);
}

.journal-expand-placeholder {
  cursor: default;
  visibility: hidden;
}

.journal-label {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 4px;
  text-align: left;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: var(--holst-text);
  padding: 6px 4px;
  border-radius: 4px;
  min-width: 0;
  overflow: hidden;
}

.journal-label-text {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

.journal-resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  touch-action: none;
  z-index: 2;
}

.journal-resize-handle::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  right: 2px;
  width: 2px;
  border-radius: 1px;
  background: transparent;
  transition: background 0.15s ease;
}

.task-journal:hover .journal-resize-handle::after,
.journal-resize-handle:active::after {
  background: var(--holst-border-strong);
}

.journal-kind {
  flex-shrink: 0;
  font-size: 12px;
}

.journal-label:hover {
  background: var(--holst-bg-muted);
}
</style>
