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
        await axios.delete(`/api/task-links/${linkId}`)
        this.taskLinks = this.taskLinks.filter(l => l.id !== linkId)
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

      await this.createTaskLink({
        source_id: taskId,
        target_id: otherId,
        link_target_type: otherType === 'note' ? 'note' : 'task',
        link_type: 'depends_on'
      })
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
