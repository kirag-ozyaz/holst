<template>
  <button
    type="button"
    class="theme-toggle"
    :title="themeStore.isDark ? 'Включить светлую тему' : 'Включить тёмную тему'"
    :aria-label="themeStore.isDark ? 'Светлая тема' : 'Тёмная тема'"
    @click="themeStore.toggle()"
  >
    <span class="theme-toggle-icon" aria-hidden="true">{{ themeStore.isDark ? '☀️' : '🌙' }}</span>
    <span class="theme-toggle-label">{{ themeStore.isDark ? 'Светлая' : 'Тёмная' }}</span>
  </button>
</template>

<script setup>
import { useThemeStore } from '../stores/theme';

const themeStore = useThemeStore();
</script>

<style scoped>
.theme-toggle {
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 1002;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--holst-border);
  background: var(--holst-bg-surface);
  color: var(--holst-text);
  font-size: 13px;
  cursor: pointer;
  box-shadow: var(--holst-shadow-sm);
}

.theme-toggle:hover {
  background: var(--holst-bg-muted);
}

.theme-toggle-icon {
  font-size: 15px;
  line-height: 1;
}
</style>
