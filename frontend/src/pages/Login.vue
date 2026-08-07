<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value.trim() || !password.value || loading.value) return
  loading.value = true
  error.value = ''
  try {
    await login(username.value, password.value)
    router.push('/')
  } catch {
    error.value = '登录失败，用户名或密码错误'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="page-shell auth-page">
    <form class="auth-card brick-band" @submit.prevent="handleLogin">
      <h1>登录</h1>
      <label>
        <span>用户名</span>
        <input v-model="username" autocomplete="username" />
      </label>
      <label>
        <span>密码</span>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
        />
      </label>
      <button
        type="submit"
        class="brick-btn brick-btn--red"
        :disabled="loading"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </main>
</template>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  padding-top: 48px;
  padding-bottom: 48px;
}

.auth-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  max-width: 420px;
  padding: 26px;
  background: var(--yellow);
}

.auth-card h1 {
  margin: 0;
  font-size: 26px;
}

.auth-card label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  font-weight: 800;
}
</style>
