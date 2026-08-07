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
  <header>
    <router-link to="/" class="brand">我的 Agent 博客</router-link>
    <nav>
      <router-link v-if="isLoggedIn" to="/new">写文章</router-link>
      <router-link v-if="isLoggedIn" to="/assistant">AI 助理</router-link>
      <router-link v-if="!isLoggedIn" to="/login">登录</router-link>
      <button v-if="isLoggedIn" @click="logout">退出</button>
    </nav>
  </header>
  <router-view />
</template>

<style scoped>
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 720px;
  margin: 0 auto;
  padding: 16px 24px;
}
nav {
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>