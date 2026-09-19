<template>
  <div
    v-if="menu"
    class="canvas-context-menu"
    :style="{ left: `${menu.clientX}px`, top: `${menu.clientY}px` }"
    role="menu"
    @contextmenu.prevent
    @click.stop
  >
    <button
      v-for="item in items"
      :key="item.id"
      type="button"
      class="ctx-item"
      :class="{ 'ctx-item-danger': item.danger, 'ctx-item-disabled': item.disabled }"
      :disabled="item.disabled"
      @click="run(item)"
    >
      {{ item.label }}
    </button>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useCanvasStore } from '../stores/canvas'

const canvasStore = useCanvasStore()

const menu = computed(() => canvasStore.contextMenu)

const items = computed(() => {
  if (!menu.value?.element) {
    return []
  }
  const el = menu.value.element
  const peer = menu.value.previousSelection
  const selOther = peer && peer.id !== el.id ? peer : null
  const list = []

  list.push({ id: 'edit', label: 'Редактировать', action: 'edit' })
  list.push({ id: 'front', label: 'На передний план', action: 'front' })

  if (el.type === 'task') {
    list.push({ id: 'sep1', label: '—', disabled: true })
    list.push({
      id: 'child-of-selected',
      label: 'Подчинить выбранному',
      action: 'child-of-selected',
      disabled: !(selOther && selOther.type === 'task')
    })
    list.push({
      id: 'parent-of-selected',
      label: 'Сделать родителем выбранного',
      action: 'parent-of-selected',
      disabled: !(selOther && selOther.type === 'task')
    })
    if (el.parent_id) {
      list.push({
        id: 'clear-parent',
        label: 'Отвязать от родителя',
        action: 'clear-parent'
      })
    }
  }

  if (el.type === 'note') {
    list.push({ id: 'sep2', label: '—', disabled: true })
    list.push({
      id: 'attach-task',
      label: 'Привязать к выбранной задаче',
      action: 'attach-task',
      disabled: !(selOther && selOther.type === 'task')
    })
    if (el.task_id) {
      list.push({
        id: 'detach-task',
        label: 'Отвязать от задачи',
        action: 'detach-task'
      })
    }
  }

  list.push({ id: 'sep3', label: '—', disabled: true })
  list.push({
    id: 'link-selected',
    label: 'Связать с выбранным',
    action: 'link-selected',
    disabled: !selOther
  })
  list.push({ id: 'link-mode', label: 'Режим связи (с этой карточки)', action: 'link-mode' })
  list.push({ id: 'sep4', label: '—', disabled: true })
  list.push({ id: 'delete', label: 'Удалить', action: 'delete', danger: true })

  return list
})

async function run(item) {
  if (item.disabled || item.label === '—') {
    return
  }
  const el = menu.value.element
  const peer = menu.value.previousSelection
  const selOther = peer && peer.id !== el.id ? peer : null

  try {
    switch (item.action) {
      case 'edit':
        canvasStore.setSelectedElement(el)
        break
      case 'front':
        await canvasStore.bringElementToFront(el)
        break
      case 'child-of-selected':
        await canvasStore.setTaskParent(el.id, selOther.id)
        break
      case 'parent-of-selected':
        await canvasStore.setTaskParent(selOther.id, el.id)
        break
      case 'clear-parent':
        await canvasStore.setTaskParent(el.id, null)
        break
      case 'attach-task':
        await canvasStore.attachNoteToTask(selOther.id, el.id)
        break
      case 'detach-task':
        if (el.task_id) {
          await canvasStore.detachNoteFromTask(el.task_id, el.id)
        }
        break
      case 'link-selected':
        if (!selOther) {
          throw new Error('Сначала выделите другой элемент (ЛКМ)')
        }
        await canvasStore.createLinkBetween(
          { id: selOther.id, type: selOther.type },
          { id: el.id, type: el.type }
        )
        break
      case 'link-mode':
        canvasStore.linkMode = true
        canvasStore.pendingLinkSource = { id: el.id, type: el.type }
        break
      case 'delete':
        if (window.confirm(el.type === 'task' ? 'Удалить задачу?' : 'Удалить заметку?')) {
          await canvasStore.deleteElement(el)
        }
        break
      default:
        break
    }
  } catch (err) {
    alert(err.message || 'Не удалось выполнить действие')
  } finally {
    canvasStore.closeContextMenu()
  }
}

function onDocClick() {
  canvasStore.closeContextMenu()
}

function onKeyDown(e) {
  if (e.key === 'Escape') {
    canvasStore.closeContextMenu()
  }
}

watch(menu, (value) => {
  if (value) {
    window.addEventListener('click', onDocClick, { capture: true })
    window.addEventListener('keydown', onKeyDown)
  } else {
    window.removeEventListener('click', onDocClick, { capture: true })
    window.removeEventListener('keydown', onKeyDown)
  }
})

onUnmounted(() => {
  window.removeEventListener('click', onDocClick, { capture: true })
  window.removeEventListener('keydown', onKeyDown)
})
</script>

<style scoped>
.canvas-context-menu {
  position: fixed;
  z-index: 2000;
  min-width: 240px;
  max-width: 320px;
  padding: 6px 0;
  background: var(--holst-bg-surface);
  border: 1px solid var(--holst-border);
  border-radius: 8px;
  box-shadow: var(--holst-shadow-md);
}

.ctx-item {
  display: block;
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  color: var(--holst-text);
  font-size: 13px;
  padding: 8px 14px;
  cursor: pointer;
}

.ctx-item:hover:not(:disabled) {
  background: var(--holst-bg-muted);
}

.ctx-item-disabled,
.ctx-item:disabled {
  color: var(--holst-text-muted);
  cursor: default;
  opacity: 0.55;
}

.ctx-item-danger {
  color: #dc2626;
}

.ctx-item-danger:hover:not(:disabled) {
  background: rgba(220, 38, 38, 0.08);
}
</style>
