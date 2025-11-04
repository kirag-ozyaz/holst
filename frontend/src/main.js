import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import './assets/styles.css'
import router from './router'
import Konva from 'konva'

// Радикальный фикс Vue + Konva - отключаем реактивность
import { markRaw } from 'vue';

// Перехватываем создание всех Konva объектов
const konvaClasses = ['Stage', 'Layer', 'Group', 'Rect', 'Text', 'Line', 'Circle', 'Image'];

konvaClasses.forEach(className => {
  if (Konva[className]) {
    const OriginalClass = Konva[className];
    Konva[className] = function(...args) {
      const instance = new OriginalClass(...args);
      return markRaw(instance);
    };
    Object.setPrototypeOf(Konva[className], OriginalClass);
    Object.assign(Konva[className], OriginalClass);
  }
});

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')