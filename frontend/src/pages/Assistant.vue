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
  <main class="page-shell assistant-page">
    <h1>AI 助理</h1>

    <div class="chat-box brick-band">
      <div class="messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['bubble', message.role === 'user' ? 'bubble--user' : 'bubble--assistant']"
        >
          {{ message.content }}
        </div>
        <p v-if="loading" class="thinking">思考中...</p>
      </div>

      <div v-if="currentSources.length" class="sources">
        <h2>参考资料</h2>
        <ul>
          <li v-for="source in currentSources" :key="source.title">
            <strong>{{ source.title }}</strong> — {{ source.snippet }}
          </li>
        </ul>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <form class="input-row" @submit.prevent="handleSend">
        <input
          v-model="input"
          placeholder="问我关于你笔记的问题..."
          :disabled="loading"
        />
        <button type="submit" class="brick-btn brick-btn--purple" :disabled="loading">
          {{ loading ? '思考中' : '发送' }}
        </button>
      </form>
    </div>
  </main>
</template>

<style scoped>
.assistant-page {
  padding-top: 28px;
  padding-bottom: 56px;
}

.assistant-page h1 {
  margin: 0 0 18px;
  font-size: 28px;
}

.chat-box {
  padding: 16px;
  background: #fff;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 220px;
  max-height: 52svh;
  overflow-y: auto;
  padding: 4px;
}

.bubble {
  max-width: 82%;
  padding: 12px 14px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  white-space: pre-wrap;
  line-height: 1.7;
}

.bubble--user {
  align-self: flex-end;
  background: var(--blue);
  color: #fff;
}

.bubble--assistant {
  align-self: flex-start;
  background: var(--yellow);
}

.thinking {
  color: var(--muted);
  font-weight: 700;
}

.sources {
  margin-top: 14px;
  padding: 12px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: var(--paper);
}

.sources h2 {
  margin: 0 0 8px;
  font-size: 15px;
}

.sources ul {
  margin: 0;
  padding-left: 20px;
}

.sources li {
  margin: 4px 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

.input-row {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.input-row input {
  flex: 1;
}
</style>
