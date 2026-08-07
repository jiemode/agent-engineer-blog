<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { clearToken, getToken } from './api/auth'

const router = useRouter()
const isLoggedIn = ref(Boolean(getToken()))

router.afterEach(() => {
  isLoggedIn.value = Boolean(getToken())
})

function logout() {
  clearToken()
  isLoggedIn.value = false
  router.push('/')
}
</script>

<template>
  <div class="site">
    <header class="site-header">
      <div class="header-inner page-shell">
        <router-link to="/" class="brand">
          <span class="logo-brick" aria-hidden="true">
            <span class="stud"></span>
            <span class="stud"></span>
            <span class="stud"></span>
            <span class="stud"></span>
          </span>
          <span class="brand-name">Agent Blog</span>
        </router-link>

        <nav class="header-nav" aria-label="主导航">
          <router-link to="/assistant" class="nav-link">AI 助理</router-link>
          <router-link v-if="isLoggedIn" to="/new" class="brick-btn brick-btn--red">
            写文章
          </router-link>
          <router-link v-else to="/login" class="brick-btn brick-btn--red">
            登录
          </router-link>
          <button v-if="isLoggedIn" class="nav-link nav-link--button" @click="logout">
            退出
          </button>
        </nav>
      </div>
      <div class="stud-strip" aria-hidden="true"></div>
    </header>

    <router-view />
  </div>
</template>

<style scoped>
.site {
  min-height: 100svh;
}

.site-header {
  background: var(--paper);
  border-bottom: 2px solid var(--ink);
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 14px;
  padding-bottom: 14px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--ink);
  font-weight: 900;
  font-size: 18px;
  text-decoration: none;
}

.logo-brick {
  display: grid;
  grid-template-columns: repeat(2, 12px);
  gap: 3px;
  padding: 5px;
  background: var(--red);
  border: 2px solid var(--ink);
  border-radius: 2px;
}

.stud {
  width: 12px;
  height: 12px;
  border: 2px solid var(--ink);
  border-radius: 50%;
  background: var(--yellow);
  box-shadow:
    inset 2px 2px 0 rgba(255, 255, 255, 0.85),
    inset -2px -2px 0 rgba(0, 0, 0, 0.18);
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.nav-link {
  padding: 6px 2px;
  color: var(--ink);
  font-size: 15px;
  font-weight: 800;
  text-decoration: none;
}

.nav-link:hover {
  text-decoration: underline;
  text-underline-offset: 4px;
}

.nav-link--button {
  background: none;
  border: none;
  cursor: pointer;
}

.stud-strip {
  margin-top: -2px;
}
</style>
