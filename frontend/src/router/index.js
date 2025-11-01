import { createRouter, createWebHistory } from 'vue-router'
import CanvasView from '../views/CanvasView.vue'
import GraphView from '../views/GraphView.vue'

const routes = [
  {
    path: '/',
    name: 'Canvas',
    component: CanvasView
  },
  {
    path: '/graph',
    name: 'Graph',
    component: GraphView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router