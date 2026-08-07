<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import { createPost } from '../api/posts'

const router = useRouter()
const title = ref('')
const content = ref('')
const tags = ref('')
const error = ref('')
const loading = ref(false)

const canSubmit = computed(
  () =>
    title.value.trim().length > 0 &&
    content.value.trim().length > 0 &&
    !loading.value,
)

async function handleCreate() {
  if (!canSubmit.value) return
  loading.value = true
  error.value = ''
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
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="page-shell editor-page">
    <h1>写文章</h1>

    <input v-model="title" placeholder="标题" class="title-input" />

    <div class="editor-grid">
      <textarea
        v-model="content"
        placeholder="支持 Markdown：标题、加粗、代码块"
        rows="16"
      ></textarea>
      <div class="preview-panel brick-band">
        <h2>预览</h2>
        <MarkdownRenderer :content="content" />
      </div>
    </div>

    <input
      v-model="tags"
      placeholder="标签，用逗号分隔，例如：python,fastapi"
    />

    <div class="editor-actions">
      <button
        class="brick-btn brick-btn--green"
        :disabled="!canSubmit"
        @click="handleCreate"
      >
        {{ loading ? '发布中...' : '发布' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </main>
</template>

<style scoped>
.editor-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-top: 28px;
  padding-bottom: 56px;
}

.editor-page h1 {
  margin: 0;
  font-size: 28px;
}

.title-input {
  font-size: 18px;
  font-weight: 800;
}

.editor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

textarea {
  font-family: ui-monospace, Consolas, monospace;
}

.preview-panel {
  padding: 12px 14px;
  background: #fff;
  overflow-wrap: anywhere;
}

.preview-panel h2 {
  margin: 0 0 8px;
  font-size: 16px;
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.editor-actions .error {
  margin: 0;
}

@media (max-width: 720px) {
  .editor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
