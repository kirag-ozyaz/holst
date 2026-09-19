import axios from 'axios'
import { defineStore } from 'pinia'

export const useCanvasStore = defineStore('canvas', {
  state: () => ({
    cards: [],
    notes: [],
    taskLinks: [],
    noteLinks: [],
    selectedElement: null,
    linkMode: false,
    pendingLinkSource: null,
    scale: 1,
    x: 0,
    y: 0
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
        return response.data
      } catch (error) {
        console.error('Error updating card:', error)
        throw error
      }
    },

    async deleteCard(cardId) {
      try {
        await axios.delete(`/api/cards/${cardId}`)
        this.cards = this.cards.filter(card => card.id !== cardId)
        this.taskLinks = this.taskLinks.filter(
          l => l.source_id !== cardId && l.target_id !== cardId
        )
        if (this.selectedElement?.id === cardId) {
          this.selectedElement = null
        }
      } catch (error) {
        console.error('Error deleting card:', error)
        throw error
      }
    },

    async createNote(noteData) {
      try {
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
        return response.data
      } catch (error) {
        console.error('Error updating note:', error)
        throw error
      }
    },

    async deleteNote(noteId) {
      try {
        await axios.delete(`/api/notes/${noteId}`)
        this.notes = this.notes.filter(note => note.id !== noteId)
        this.taskLinks = this.taskLinks.filter(
          l => l.source_id !== noteId && l.target_id !== noteId
        )
        this.noteLinks = this.noteLinks.filter(
          l => l.source_id !== noteId && l.target_id !== noteId
        )
        if (this.selectedElement?.id === noteId) {
          this.selectedElement = null
        }
      } catch (error) {
        console.error('Error deleting note:', error)
        throw error
      }
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
        await axios.delete(`/api/note-links/${linkId}`)
        this.noteLinks = this.noteLinks.filter(l => l.id !== linkId)
      } catch (error) {
        console.error('Error deleting note link:', error)
        throw error
      }
    },

    setSelectedElement(element) {
      this.selectedElement = element
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
          ids.add(link.target_id)
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
      await this.updateNote(noteId, { task_id: taskId })
      await this.ensureTaskNoteLink(taskId, noteId)
    },

    async detachNoteFromTask(taskId, noteId) {
      const note = this.notes.find(n => n.id === noteId)
      if (note && note.task_id === taskId) {
        await this.updateNote(noteId, { task_id: null })
      }
      const link = this.findTaskNoteLink(taskId, noteId)
      if (link) {
        await this.deleteTaskLink(link.id)
      }
    },

    async createNoteForTask(taskId, overrides = {}) {
      const pos = overrides.x != null && overrides.y != null
        ? { x: overrides.x, y: overrides.y }
        : { x: Math.round(120 + Math.random() * 400), y: Math.round(120 + Math.random() * 400) }
      const note = await this.createNote({
        title: overrides.title || 'Новая заметка',
        content: overrides.content ?? [],
        task_id: taskId,
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
          await this.updateNote(otherId, { task_id: taskId })
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
    }
  }
})
