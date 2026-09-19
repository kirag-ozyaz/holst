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
          :key="row.task.id"
          class="journal-row"
          :class="{
            'journal-row-selected': isSelected(row.task.id),
            'journal-row-has-children': row.hasChildren
          }"
          :style="{ paddingLeft: `${12 + row.depth * 16}px` }"
        >
          <button
            v-if="row.hasChildren"
            type="button"
            class="journal-chevron"
            :aria-expanded="row.expanded"
            :title="row.expanded ? 'Свернуть' : 'Развернуть'"
            @click.stop="toggleExpand(row.task.id)"
          >
            {{ row.expanded ? '▾' : '▸' }}
          </button>
          <span v-else class="journal-chevron journal-chevron-placeholder" aria-hidden="true" />

          <button
            type="button"
            class="journal-label"
            @click="onRowActivate(row)"
          >
            {{ row.task.title || 'Без названия' }}
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
const expandedIds = ref(new Set());

function sortTasks(tasks) {
  return [...tasks].sort((a, b) =>
    (a.title || '').localeCompare(b.title || '', 'ru', { sensitivity: 'base' })
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
    map.set(key, sortTasks(list));
  });
  return map;
});

const rootTasks = computed(() => {
  const ids = new Set(canvasStore.cards.map(c => c.id));
  const roots = canvasStore.cards.filter(task => {
    if (!task.parent_id) return true;
    return !ids.has(task.parent_id);
  });
  return sortTasks(roots);
});

function hasChildren(taskId) {
  return (childrenByParent.value.get(taskId) || []).length > 0;
}

function buildVisibleRows(tasks, depth, out) {
  for (const task of tasks) {
    const expanded = expandedIds.value.has(task.id);
    const childList = childrenByParent.value.get(task.id) || [];
    out.push({
      task,
      depth,
      hasChildren: childList.length > 0,
      expanded
    });
    if (childList.length > 0 && expanded) {
      buildVisibleRows(childList, depth + 1, out);
    }
  }
}

const visibleRows = computed(() => {
  const rows = [];
  buildVisibleRows(rootTasks.value, 0, rows);
  return rows;
});

function toggleExpand(taskId) {
  const next = new Set(expandedIds.value);
  if (next.has(taskId)) {
    next.delete(taskId);
  } else {
    next.add(taskId);
  }
  expandedIds.value = next;
}

function onRowActivate(row) {
  if (row.hasChildren) {
    toggleExpand(row.task.id);
  }
  selectTask(row.task.id);
}

function selectTask(taskId) {
  const card = canvasStore.cards.find(c => c.id === taskId);
  if (card) {
    canvasStore.setSelectedElement({ ...card, type: 'task' });
  }
}

function isSelected(taskId) {
  return (
    canvasStore.selectedElement?.type === 'task' &&
    canvasStore.selectedElement?.id === taskId
  );
}

watch(
  () => canvasStore.cards.map(c => c.id).join(','),
  () => {
    const ids = new Set(canvasStore.cards.map(c => c.id));
    const next = new Set();
    expandedIds.value.forEach(id => {
      if (ids.has(id)) next.add(id);
    });
    expandedIds.value = next;
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

.journal-chevron {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--holst-text-muted);
  font-size: 12px;
  border-radius: 4px;
}

.journal-chevron:hover {
  background: var(--holst-bg-muted);
}

.journal-chevron-placeholder {
  cursor: default;
  visibility: hidden;
}

.journal-label {
  flex: 1;
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

.journal-label:hover {
  background: var(--holst-bg-muted);
}
</style>
