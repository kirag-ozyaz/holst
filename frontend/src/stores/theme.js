import { defineStore } from 'pinia'

const STORAGE_KEY = 'holst-theme'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    theme: 'light'
  }),

  getters: {
    isDark: state => state.theme === 'dark'
  },

  actions: {
    init() {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved === 'light' || saved === 'dark') {
        this.theme = saved
      } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        this.theme = 'dark'
      } else {
        this.theme = 'light'
      }
      this.apply()
    },

    toggle() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      localStorage.setItem(STORAGE_KEY, this.theme)
      this.apply()
    },

    apply() {
      document.documentElement.setAttribute('data-theme', this.theme)
    }
  }
})
