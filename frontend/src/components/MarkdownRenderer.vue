<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps<{ content: string }>()

const html = computed(() => {
  const rawHtml = marked.parse(props.content, { async: false }) as string
  return DOMPurify.sanitize(rawHtml)
})
</script>

<template>
  <div class="markdown-body" v-html="html"></div>
</template>

<style scoped>
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 16px 0 8px;
}
.markdown-body :deep(p) {
  margin: 8px 0;
  line-height: 1.7;
}
.markdown-body :deep(pre) {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}
.markdown-body :deep(code) {
  background: #f5f5f5;
  padding: 2px 5px;
  border-radius: 4px;
}
.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
}
.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 24px;
}
.markdown-body :deep(blockquote) {
  border-left: 4px solid #ddd;
  margin: 8px 0;
  padding-left: 12px;
  color: #666;
}
</style>