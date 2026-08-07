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

// GitHub Pages 会把站点部署在子路径 /agent-engineer-blog/ 下，
// 所以 Router 必须使用 Vite 的 BASE_URL 作为 base，否则根路由匹配不到。
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  if (to.path === '/new' && !localStorage.getItem('access_token')) {
    return '/login'
  }
})

export default router
