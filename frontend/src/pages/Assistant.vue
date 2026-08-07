<script setup lang="ts">
import { ref } from 'vue'
import { askAssistantStream, type AssistantSource } from '../api/assistant'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

const input = ref('')
const messages = ref<ChatMessage[]>([])
const loading = ref(false)
const error = ref('')
const currentSources = ref<AssistantSource[]>([])

async function handleSend() {
  const question = input.value.trim()
  if (!question || loading.value) return
  input.value = ''
  error.value = ''
  currentSources.value = []

  messages.value.push({ role: 'user', content: question })
  messages.value.push({ role: 'assistant', content: '' })

  const history = messages.value
    .slice(0, -1)
    .filter((message) => message.content)
    .map((message) => ({ role: message.role, content: message.content }))

  loading.value = true
  const assistantMessage = messages.value[messages.value.length - 1]

  try {
    const answer = await askAssistantStream(
      question,
      history,
      (text) => {
        assistantMessage.content = text
      },
      (sources) => {
        currentSources.value = sources
      },
    )
    assistantMessage.content = answer
  } catch {
    assistantMessage.content = '出错了，请稍后再试'
    error.value = '提问失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="chat">
    <h1>我的 AI 助理</h1>

    <div class="messages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['bubble', message.role]"
      >
        {{ message.content }}
      </div>
      <p v-if="loading">思考中...</p>
    </div>

    <div v-if="currentSources.length" class="sources">
      <h3>参考资料</h3>
      <ul>
        <li v-for="source in currentSources" :key="source.title">
          <strong>{{ source.title }}</strong> — {{ source.snippet }}
        </li>
      </ul>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="input-row">
      <input
        v-model="input"
        placeholder="问我关于你笔记的问题..."
        @keyup.enter="handleSend"
      />
      <button @click="handleSend" :disabled="loading">发送</button>
    </div>
  </main>
</template>

<style scoped>
.chat {
  max-width: 720px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.messages {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 200px;
}
.bubble {
  padding: 12px;
  border-radius: 8px;
  max-width: 80%;
  white-space: pre-wrap;
  line-height: 1.7;
}
.bubble.user {
  align-self: flex-end;
  background: #0070f3;
  color: white;
}
.bubble.assistant {
  align-self: flex-start;
  background: #f0f0f0;
}
.input-row {
  display: flex;
  gap: 8px;
}
.input-row input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
}
.sources {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
}
.error {
  color: red;
}
</style>