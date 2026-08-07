import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Login from '../pages/Login.vue'
import NewPost from '../pages/NewPost.vue'
import Assistant from '../pages/Assistant.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/new', component: NewPost },
  { path: '/assistant', component: Assistant },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.path === '/new' && !localStorage.getItem('access_token')) {
    return '/login'
  }
})

export default router