<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  try {
    await login(username.value, password.value)
    router.push('/')
  } catch {
    error.value = '登录失败，用户名或密码错误'
  }
}
</script>

<template>
  <main class="login">
    <h1>登录</h1>
    <input v-model="username" placeholder="用户名" />
    <input v-model="password" type="password" placeholder="密码" />
    <button @click="handleLogin">登录</button>
    <p v-if="error" class="error">{{ error }}</p>
  </main>
</template>

<style scoped>
.login {
  max-width: 360px;
  margin: 80px auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
input {
  padding: 10px;
}
.error {
  color: red;
}
</style>