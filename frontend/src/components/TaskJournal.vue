<template>
  <aside class="task-journal" aria-label="Журнал задач">
    <div class="journal-header">
      <h2 class="journal-title">Журнал задач</h2>
      <button type="button" class="journal-toggle" @click="collapsed = !collapsed">
        {{ collapsed ? '▸' : '▾' }}
      </button>
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
            'journal-row-has-children': row.hasChildren,
            'journal-row-note': row.kind === 'note'
          }"
          :style="{ paddingLeft: `${12 + row.depth * 16}px` }"
        >
          <button
            v-if="row.hasChildren"
            type="button"
            class="journal-expand"
            :aria-expanded="row.expanded"
            :title="row.expanded ? 'Свернуть' : 'Развернуть'"
            @click.stop="toggleExpand(row.key)"
          >
            {{ row.expanded ? '➖' : '➕' }}
          </button>
          <span v-else class="journal-expand journal-expand-placeholder" aria-hidden="true" />

          <button
            type="button"
            class="journal-label"
            @click="onRowSelect(row)"
          >
            <span v-if="row.kind === 'note'" class="journal-kind" aria-hidden="true">📝</span>
            {{ row.title || 'Без названия' }}
          </button>
        </li>
      </ul>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useCanvasStore } from '../stores/canvas';

const canvasStore = useCanvasStore();
const collapsed = ref(false);
const expandedKeys = ref(new Set());

function sortByTitle(items, getTitle) {
  return [...items].sort((a, b) =>
    (getTitle(a) || '').localeCompare(getTitle(b) || '', 'ru', { sensitivity: 'base' })
  );
}

const childrenByParent = computed(() => {
  const map = new Map();
  canvasStore.cards.forEach(task => {
    const key = task.parent_id || null;
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
    if (!task.parent_id) return true;
    return !ids.has(task.parent_id);
  });
  return sortByTitle(roots, (t) => t.title);
});

function childTasks(taskId) {
  return childrenByParent.value.get(taskId) || [];
}

/** Notes subordinate to a task via task_id (EditorPanel attach / create-and-attach). */
function childNotesOfTask(taskId) {
  const notes = canvasStore.notes.filter((n) => n.task_id === taskId);
  return sortByTitle(notes, (n) => n.title);
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
    out.push({
      key: `note:${note.id}`,
      kind: 'note',
      id: note.id,
      title: note.title,
      depth: depth + 1,
      hasChildren: false,
      expanded: false
    });
  }
}

const visibleRows = computed(() => {
  const rows = [];
  for (const task of rootTasks.value) {
    pushTaskRows(task, 0, rows);
  }
  return rows;
});

function toggleExpand(key) {
  const next = new Set(expandedKeys.value);
  if (next.has(key)) {
    next.delete(key);
  } else {
    next.add(key);
  }
  expandedKeys.value = next;
}

function onRowSelect(row) {
  if (row.kind === 'task') {
    const card = canvasStore.cards.find(c => c.id === row.id);
    if (card) {
      canvasStore.setSelectedElement({ ...card, type: 'task' });
    }
    return;
  }
  const note = canvasStore.notes.find(n => n.id === row.id);
  if (note) {
    canvasStore.setSelectedElement({ ...note, type: 'note' });
  }
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
      canvasStore.notes.map(n => `${n.id}:${n.task_id || ''}`).join(',')
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
  width: 300px;
  max-height: calc(100vh - 90px);
  background: var(--holst-bg-surface);
  color: var(--holst-text);
  border-radius: 8px;
  box-shadow: var(--holst-shadow-md);
  border: 1px solid var(--holst-border);
  z-index: 999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.journal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--holst-border);
}

.journal-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--holst-text);
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
  text-overflow: ellipsis;
  white-space: nowrap;
}

.journal-kind {
  flex-shrink: 0;
  font-size: 12px;
}

.journal-label:hover {
  background: var(--holst-bg-muted);
}
</style>
