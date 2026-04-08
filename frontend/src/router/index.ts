import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'Dashboard' },
  },
  {
    path: '/records',
    name: 'Records',
    component: () => import('@/views/Records.vue'),
    meta: { title: 'Health Records' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis.vue'),
    meta: { title: 'Plateau Analysis' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  const title = typeof to.meta.title === 'string' ? to.meta.title : 'PlateauBreaker'
  document.title = `${title} | PlateauBreaker`
})

export default router
