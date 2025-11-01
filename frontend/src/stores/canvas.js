import axios from 'axios'
import { defineStore } from 'pinia'

export const useCanvasStore = defineStore('canvas', {
  state: () => ({
    cards: [],
    notes: [],
    taskLinks: [],
    noteLinks: [],
    selectedElement: null,
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
          this.cards[index] = response.data
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
      } catch (error) {
        console.error('Error deleting card:', error)
        throw error
      }
    },

    async createNote(noteData) {
      try {
        const response = await axios.post('/api/notes', noteData)
        this.notes.push(response.data)
        return response.data
      } catch (error) {
        console.error('Error creating note:', error)
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

    setSelectedElement(element) {
      this.selectedElement = element
    },

    setTransform(scale, x, y) {
      this.scale = scale
      this.x = x
      this.y = y
    }
  }
})