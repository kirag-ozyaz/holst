import axios from 'axios'
import { defineStore } from 'pinia'
import { wouldCreateTaskParentCycle } from '../utils/taskHierarchy.js'

export const useCanvasStore = defineStore('canvas', {
  state: () => ({
    cards: [],
    notes: [],
    taskLinks: [],
    noteLinks: [],
    selectedElement: null,
    highlightedLinkKey: null,
    linkPeerElementId: null,
    linkMode: false,
    pendingLinkSource: null,
    scale: 1,
    x: 0,
    y: 0,
    editorAnchor: null,
    editorElement: null,
    editorPanelPosition: null,
    contextMenu: null
  }),

  actions: {
    async loadData() {
      try {
        const [cardsRes, notesRes, taskLinksRes, noteLinksRes] = await Promise.all([
          axios.get('/api/cards'),
          axios.get('/api/notes'),
          axios.get('/api/task-links'),
          axios.get('/api/note-links')
        ])
        this.cards = cardsRes.data
        this.notes = notesRes.data
        this.taskLinks = taskLinksRes.data
        this.noteLinks = noteLinksRes.data
      } catch (error) {
        console.error('Error loading data:', error)
      }
    },

    async createCard(cardData) {
      try {
        if (cardData.parent_id && cardData.z_index === undefined) {
          const parentZ = this.taskZIndex(cardData.parent_id)
          if (parentZ != null) {
            cardData.z_index = parentZ
          }
        }
        if (cardData.z_index === undefined) {
          const maxZResponse = await axios.get('/api/max-z-index')
          cardData.z_index = maxZResponse.data.max_z_index + 1
        }
        const response = await axios.post('/api/cards', cardData)
        this.cards.push(response.data)
        return response.data
      } catch (error) {
        console.error('Error creating card:', error)
        throw error
      }
    },

    async updateCard(cardId, cardData) {
      try {
        const response = await axios.put(`/api/cards/${cardId}`, cardData)
        const index = this.cards.findIndex(card => card.id === cardId)
        if (index !== -1) {
          Object.assign(this.cards[index], response.data)
        }
        if (this.selectedElement?.id === cardId) {
          this.selectedElement = { ...this.selectedElement, ...response.data, type: 'task' }
        }
        if (this.editorElement?.id === cardId) {
          this.editorElement = { ...this.editorElement, ...response.data, type: 'task' }
        }
        return response.data
      } catch (error) {
        console.error('Error updating card:', error)
        throw error
      }
    },

    async deleteCard(cardId, options = {}) {
      try {
        const params = options.cascade ? { cascade: true } : undefined
        await axios.delete(`/api/cards/${cardId}`, { params })
        this.removeTaskFromState(cardId, options.cascade)
      } catch (error) {
        console.error('Error deleting card:', error)
        throw error
      }
    },

    async deleteCardCascade(cardId) {
      return this.deleteCard(cardId, { cascade: true })
    },

    removeTaskFromState(cardId, cascade) {
      let removedTaskIds = new Set([cardId])
      let removedNoteIds = new Set()
      if (cascade) {
        const subtree = this.collectTaskSubtree(cardId)
        removedTaskIds = subtree.taskIds
        removedNoteIds = subtree.noteIds
        this.cards = this.cards.filter(card => !removedTaskIds.has(card.id))
        this.notes = this.notes.filter(note => !removedNoteIds.has(note.id))
        this.taskLinks = this.taskLinks.filter(
          l =>
            !removedTaskIds.has(l.source_id) &&
            !removedTaskIds.has(l.target_id) &&
            !removedNoteIds.has(l.target_id) &&
            !removedNoteIds.has(l.source_id)
        )
        this.noteLinks = this.noteLinks.filter(
          l => !removedNoteIds.has(l.source_id) && !removedNoteIds.has(l.target_id)
        )
      } else {
        this.cards = this.cards.filter(card => card.id !== cardId)
        this.taskLinks = this.taskLinks.filter(
          l => l.source_id !== cardId && l.target_id !== cardId
        )
      }
      const sel = this.selectedElement
      if (
        sel &&
        (removedTaskIds.has(sel.id) ||
          (sel.type === 'note' && removedNoteIds.has(sel.id)))
      ) {
        this.selectedElement = null
        this.closeEditor()
      }
      this.closeContextMenu()
    },

    async createNote(noteData) {
      try {
        if (noteData.task_id && noteData.z_index === undefined) {
          const parentZ = this.taskZIndex(noteData.task_id)
          if (parentZ != null) {
            noteData.z_index = parentZ
          }
        }
        if (noteData.z_index === undefined) {
          const maxZResponse = await axios.get('/api/max-z-index')
          noteData.z_index = maxZResponse.data.max_z_index + 1
        }
        const response = await axios.post('/api/notes', noteData)
        this.notes.push(response.data)
        return response.data
      } catch (error) {
        console.error('Error creating note:', error)
        throw error
      }
    },

    async updateNote(noteId, noteData) {
      try {
        const response = await axios.put(`/api/notes/${noteId}`, noteData)
        const index = this.notes.findIndex(note => note.id === noteId)
        if (index !== -1) {
          Object.assign(this.notes[index], response.data)
        }
        if (this.selectedElement?.id === noteId) {
          this.selectedElement = { ...this.selectedElement, ...response.data, type: 'note' }
        }
        if (this.editorElement?.id === noteId) {
          this.editorElement = { ...this.editorElement, ...response.data, type: 'note' }
        }
        return response.data
      } catch (error) {
        console.error('Error updating note:', error)
        throw error
      }
    },

    async deleteNote(noteId, options = {}) {
      try {
        const params = options.cascade ? { cascade: true } : undefined
        await axios.delete(`/api/notes/${noteId}`, { params })
        this.removeNoteFromState(noteId, options.cascade)
      } catch (error) {
        console.error('Error deleting note:', error)
        throw error
      }
    },

    async deleteNoteCascade(noteId) {
      return this.deleteNote(noteId, { cascade: true })
    },

    removeNoteFromState(noteId, cascade) {
      const removedNoteIds = cascade ? this.collectNoteSubtree(noteId) : new Set([noteId])
      if (cascade) {
        this.notes = this.notes.filter(note => !removedNoteIds.has(note.id))
        this.taskLinks = this.taskLinks.filter(
          l => !removedNoteIds.has(l.source_id) && !removedNoteIds.has(l.target_id)
        )
        this.noteLinks = this.noteLinks.filter(
          l => !removedNoteIds.has(l.source_id) && !removedNoteIds.has(l.target_id)
        )
      } else {
        this.notes = this.notes.filter(note => note.id !== noteId)
        this.taskLinks = this.taskLinks.filter(
          l => l.source_id !== noteId && l.target_id !== noteId
        )
        this.noteLinks = this.noteLinks.filter(
          l => l.source_id !== noteId && l.target_id !== noteId
        )
      }
      if (this.selectedElement && removedNoteIds.has(this.selectedElement.id)) {
        this.selectedElement = null
      }
      if (this.editorElement && removedNoteIds.has(this.editorElement.id)) {
        this.closeEditor()
      }
      this.closeContextMenu()
    },

    collectTaskSubtree(taskId) {
      const taskIds = new Set()
      const queue = [taskId]
      while (queue.length) {
        const id = queue.pop()
        if (taskIds.has(id)) continue
        taskIds.add(id)
        this.cards.forEach(card => {
          if (card.parent_id === id) {
            queue.push(card.id)
          }
        })
      }
      const noteIds = new Set()
      taskIds.forEach(id => {
        this.notesAttachedToTask(id).forEach(note => noteIds.add(note.id))
      })
      return { taskIds, noteIds }
    },

    collectNoteSubtree(noteId) {
      const noteIds = new Set()
      const queue = [noteId]
      while (queue.length) {
        const id = queue.pop()
        if (noteIds.has(id)) continue
        noteIds.add(id)
        this.noteLinks.forEach(link => {
          if (link.source_id === id) {
            queue.push(link.target_id)
          }
        })
      }
      return noteIds
    },

    elementHasSubordinates(element) {
      if (!element) return false
      if (element.type === 'task') {
        const { taskIds, noteIds } = this.collectTaskSubtree(element.id)
        return taskIds.size > 1 || noteIds.size > 0
      }
      if (element.type === 'note') {
        return this.noteLinks.some(link => link.source_id === element.id)
      }
      return false
    },

    setEditorAnchor(anchor) {
      this.editorAnchor = anchor
    },

    setEditorPanelPosition(position) {
      this.editorPanelPosition = position
    },

    taskZIndex(taskId) {
      const task = this.cards.find(c => c.id === taskId)
      return task?.z_index ?? null
    },

    childTasksOf(taskId) {
      return this.cards.filter(c => c.parent_id === taskId)
    },

    async syncChildZIndices(parentTaskId, zIndex) {
      const childTasks = this.childTasksOf(parentTaskId)
      const attachedNotes = this.notesAttachedToTask(parentTaskId)
      const updates = []
      for (const child of childTasks) {
        if (child.z_index !== zIndex) {
          updates.push(this.updateCard(child.id, { z_index: zIndex }))
        }
        updates.push(this.syncChildZIndices(child.id, zIndex))
      }
      for (const note of attachedNotes) {
        if (note.z_index !== zIndex) {
          updates.push(this.updateNote(note.id, { z_index: zIndex }))
        }
      }
      await Promise.all(updates)
    },

    async syncZIndexForHierarchy(taskId, zIndex) {
      await this.syncChildZIndices(taskId, zIndex)
    },

    openEditor(element) {
      if (!element) {
        this.closeEditor()
        return
      }
      this.editorElement = { ...element }
      this.editorPanelPosition = null
    },

    closeEditor() {
      this.editorElement = null
      this.editorAnchor = null
      this.editorPanelPosition = null
    },

    async createTaskLink(linkData) {
      try {
        const response = await axios.post('/api/task-links', linkData)
        this.taskLinks.push(response.data)
        return response.data
      } catch (error) {
        console.error('Error creating task link:', error)
        throw error
      }
    },

    async deleteTaskLink(linkId) {
      try {
        const link = this.taskLinks.find(l => l.id === linkId)
        if (link && this.highlightedLinkKey === this.linkKey('task', linkId)) {
          this.clearHighlightedLink()
        }
        await axios.delete(`/api/task-links/${linkId}`)
        this.taskLinks = this.taskLinks.filter(l => l.id !== linkId)
        if (
          link &&
          (link.link_target_type === 'note' || link.link_target_type === 'card') &&
          link.target_id
        ) {
          const note = this.notes.find(n => n.id === link.target_id)
          if (note && note.task_id === link.source_id) {
            await this.updateNote(link.target_id, { task_id: null })
          }
        }
      } catch (error) {
        console.error('Error deleting task link:', error)
        throw error
      }
    },

    async createNoteLink(linkData) {
      try {
        const response = await axios.post('/api/note-links', linkData)
        this.noteLinks.push(response.data)
        return response.data
      } catch (error) {
        console.error('Error creating note link:', error)
        throw error
      }
    },

    async deleteNoteLink(linkId) {
      try {
        if (this.highlightedLinkKey === this.linkKey('note', linkId)) {
          this.clearHighlightedLink()
        }
        await axios.delete(`/api/note-links/${linkId}`)
        this.noteLinks = this.noteLinks.filter(l => l.id !== linkId)
      } catch (error) {
        console.error('Error deleting note link:', error)
        throw error
      }
    },

    linkKey(kind, id) {
      return `${kind}-${id}`
    },

    setHighlightedLink(kind, id) {
      const key = this.linkKey(kind, id)
      if (this.highlightedLinkKey === key) {
        this.clearHighlightedLink()
        return
      }
      this.highlightedLinkKey = key
      const link =
        kind === 'task'
          ? this.taskLinks.find(l => l.id === id)
          : this.noteLinks.find(l => l.id === id)
      const selectedId = this.selectedElement?.id
      if (link && selectedId) {
        this.linkPeerElementId =
          link.source_id === selectedId ? link.target_id : link.source_id
      } else {
        this.linkPeerElementId = null
      }
    },

    clearHighlightedLink() {
      this.highlightedLinkKey = null
      this.linkPeerElementId = null
    },

    setSelectedElement(element) {
      this.selectedElement = element
      this.clearHighlightedLink()
      if (!element) {
        this.closeEditor()
      }
      this.closeContextMenu()
    },

    clearSelection() {
      this.setSelectedElement(null)
    },

    toggleLinkMode() {
      this.linkMode = !this.linkMode
      this.pendingLinkSource = null
    },

    cancelLinkMode() {
      this.linkMode = false
      this.pendingLinkSource = null
    },

    async handleLinkClick(element) {
      if (!this.linkMode) {
        return
      }

      const normalized = { id: element.id, type: element.type === 'note' ? 'note' : 'task' }

      if (!this.pendingLinkSource) {
        this.pendingLinkSource = normalized
        return
      }

      const source = this.pendingLinkSource
      const target = normalized

      if (source.id === target.id) {
        this.pendingLinkSource = null
        return
      }

      try {
        await this.createLinkBetween(source, target)
      } catch (error) {
        const detail = error.response?.data?.detail
        alert(typeof detail === 'string' ? detail : 'Не удалось создать связь')
      }

      this.pendingLinkSource = null
    },

    findTaskNoteLink(taskId, noteId) {
      return this.taskLinks.find(
        l =>
          l.source_id === taskId &&
          l.target_id === noteId &&
          (l.link_target_type === 'note' || l.link_target_type === 'card')
      )
    },

    /** Visual/task_links direction: task (source) → note (target); matches link mode first→second click. */
    async ensureTaskNoteLink(taskId, noteId) {
      if (this.findTaskNoteLink(taskId, noteId)) {
        return
      }
      await this.createTaskLink({
        source_id: taskId,
        target_id: noteId,
        link_target_type: 'note',
        link_type: 'depends_on'
      })
    },

    notesAttachedToTask(taskId) {
      const ids = new Set()
      this.notes.forEach(note => {
        if (note.task_id === taskId) {
          ids.add(note.id)
        }
      })
      this.taskLinks.forEach(link => {
        if (
          link.source_id === taskId &&
          (link.link_target_type === 'note' || link.link_target_type === 'card') &&
          link.target_id
        ) {
          const note = this.notes.find(n => n.id === link.target_id)
          if (note && (!note.task_id || note.task_id === taskId)) {
            ids.add(link.target_id)
          }
        }
      })
      return this.notes.filter(n => ids.has(n.id))
    },

    notesAvailableToAttach(taskId) {
      const attached = new Set(this.notesAttachedToTask(taskId).map(n => n.id))
      return this.notes.filter(n => !attached.has(n.id))
    },

    async attachNoteToTask(taskId, noteId) {
      const note = this.notes.find(n => n.id === noteId)
      if (!note) {
        throw new Error('Заметка не найдена')
      }
      const prevTaskId = note.task_id
      if (prevTaskId && prevTaskId !== taskId) {
        const oldLink = this.findTaskNoteLink(prevTaskId, noteId)
        if (oldLink) {
          await this.deleteTaskLink(oldLink.id)
        }
      }
      const taskZ = this.taskZIndex(taskId)
      const noteUpdate = { task_id: taskId }
      if (taskZ != null) {
        noteUpdate.z_index = taskZ
      }
      await this.updateNote(noteId, noteUpdate)
      await this.ensureTaskNoteLink(taskId, noteId)
    },

    async detachNoteFromTask(taskId, noteId) {
      const link = this.findTaskNoteLink(taskId, noteId)
      if (link) {
        await this.deleteTaskLink(link.id)
      }
      const note = this.notes.find(n => n.id === noteId)
      if (note && note.task_id === taskId) {
        await this.updateNote(noteId, { task_id: null })
      }
    },

    async createNoteForTask(taskId, overrides = {}) {
      const pos = overrides.x != null && overrides.y != null
        ? { x: overrides.x, y: overrides.y }
        : { x: Math.round(120 + Math.random() * 400), y: Math.round(120 + Math.random() * 400) }
      const taskZ = this.taskZIndex(taskId)
      const note = await this.createNote({
        title: overrides.title || 'Новая заметка',
        content: overrides.content ?? [],
        task_id: taskId,
        ...(taskZ != null ? { z_index: taskZ } : {}),
        ...pos,
        ...overrides
      })
      await this.ensureTaskNoteLink(taskId, note.id)
      return note
    },

    async setNoteParentTask(noteId, taskId) {
      const note = this.notes.find(n => n.id === noteId)
      if (!note) {
        throw new Error('Заметка не найдена')
      }
      const prevTaskId = note.task_id
      const nextTaskId = taskId || null
      if (nextTaskId === prevTaskId) {
        if (nextTaskId) {
          await this.ensureTaskNoteLink(nextTaskId, noteId)
        }
        return
      }
      if (prevTaskId) {
        await this.detachNoteFromTask(prevTaskId, noteId)
      }
      if (nextTaskId) {
        await this.attachNoteToTask(nextTaskId, noteId)
      }
    },

    async createLinkBetween(source, target) {
      if (source.type === 'note' && target.type === 'note') {
        await this.createNoteLink({
          source_id: source.id,
          target_id: target.id,
          link_type: 'linked_to'
        })
        return
      }

      let taskId = source.type === 'task' ? source.id : target.id
      let otherId = source.type === 'task' ? target.id : source.id
      let otherType = source.type === 'task' ? target.type : source.type

      if (source.type !== 'task' && target.type !== 'task') {
        throw new Error('Invalid link pair')
      }

      const linkTargetType = otherType === 'note' ? 'note' : 'task'
      const existing = this.taskLinks.find(
        l =>
          l.source_id === taskId &&
          l.target_id === otherId &&
          (l.link_target_type === linkTargetType ||
            (linkTargetType === 'task' && l.link_target_type === 'card'))
      )
      if (!existing) {
        await this.createTaskLink({
          source_id: taskId,
          target_id: otherId,
          link_target_type: linkTargetType,
          link_type: 'depends_on'
        })
      }

      if (linkTargetType === 'note') {
        const note = this.notes.find(n => n.id === otherId)
        if (note && note.task_id !== taskId) {
          const taskZ = this.taskZIndex(taskId)
          await this.updateNote(otherId, {
            task_id: taskId,
            ...(taskZ != null ? { z_index: taskZ } : {})
          })
        }
      }
    },

    linksForElement(elementId) {
      const task = this.taskLinks
        .filter(l => l.source_id === elementId || l.target_id === elementId)
        .map(l => ({ ...l, kind: 'task' }))
      const note = this.noteLinks
        .filter(l => l.source_id === elementId || l.target_id === elementId)
        .map(l => ({ ...l, kind: 'note' }))
      return [...task, ...note]
    },

    getMaxZIndex() {
      let maxZ = 0
      this.cards.forEach(card => {
        if (card.z_index > maxZ) maxZ = card.z_index
      })
      this.notes.forEach(note => {
        if (note.z_index > maxZ) maxZ = note.z_index
      })
      return maxZ
    },

    setTransform(scale, x, y) {
      this.scale = scale
      this.x = x
      this.y = y
    },

    openContextMenu(clientX, clientY, element, previousSelection = null) {
      this.contextMenu = { clientX, clientY, element, previousSelection }
    },

    closeContextMenu() {
      this.contextMenu = null
    },

    async setTaskParent(taskId, parentId) {
      const parent = parentId || null
      if (wouldCreateTaskParentCycle(taskId, parent, this.cards)) {
        throw new Error('Нельзя создать циклическую иерархию задач')
      }
      await this.updateCard(taskId, { parent_id: parent })
      if (parent) {
        const parentZ = this.taskZIndex(parent)
        if (parentZ != null) {
          await this.updateCard(taskId, { z_index: parentZ })
        }
      }
    },

    async bringElementToFront(element) {
      const maxZ = this.getMaxZIndex() + 1
      if (element.type === 'task') {
        await this.updateCard(element.id, { z_index: maxZ })
        await this.syncZIndexForHierarchy(element.id, maxZ)
      } else {
        await this.updateNote(element.id, { z_index: maxZ })
      }
    },

    async persistElementZIndex(elementId, elementType, zIndex) {
      if (elementType === 'task') {
        await this.updateCard(elementId, { z_index: zIndex })
        await this.syncZIndexForHierarchy(elementId, zIndex)
      } else {
        await this.updateNote(elementId, { z_index: zIndex })
      }
    },

    async deleteElement(element, options = {}) {
      if (element.type === 'task') {
        await this.deleteCard(element.id, options)
      } else {
        await this.deleteNote(element.id, options)
      }
    },

    async deleteElementCascade(element) {
      return this.deleteElement(element, { cascade: true })
    },

    async linkElementToSelected(target) {
      const selected = this.selectedElement
      if (!selected || selected.id === target.id) {
        throw new Error('Выберите другой элемент (ЛКМ), затем выполните команду')
      }
      await this.createLinkBetween(
        { id: selected.id, type: selected.type },
        { id: target.id, type: target.type }
      )
    }
  }
})
