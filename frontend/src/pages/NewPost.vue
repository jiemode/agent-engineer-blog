<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createPost } from '../api/posts'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'

const router = useRouter()
const title = ref('')
const content = ref('')
const tags = ref('')
const error = ref('')

async function handleCreate() {
  try {
    await createPost({
      title: title.value,
      content: content.value,
      tags: tags.value
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean),
    })
    router.push('/')
  } catch {
    error.value = '创建失败，请确认已登录'
  }
}
</script>

<template>
  <main class="editor">
    <h1>写文章</h1>
    <input v-model="title" placeholder="标题" />
    <div class="editor-grid">
      <textarea v-model="content" placeholder="支持 Markdown，例如：# 标题、**加粗**、```代码```" rows="16"></textarea>
      <div class="preview">
        <h2>预览</h2>
        <MarkdownRenderer :content="content" />
      </div>
    </div>
    <input v-model="tags" placeholder="标签，用逗号分隔，例如：python,fastapi" />
    <button @click="handleCreate">发布</button>
    <p v-if="error" class="error">{{ error }}</p>
  </main>
</template>

<style scoped>
.editor {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.editor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
textarea {
  padding: 10px;
  font-size: 16px;
  font-family: monospace;
}
.preview {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
}
input {
  padding: 10px;
  font-size: 16px;
}
.error {
  color: red;
}
</style>