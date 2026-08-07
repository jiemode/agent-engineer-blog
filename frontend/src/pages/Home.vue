<script setup lang="ts">
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import { computed, onMounted, ref } from 'vue'
import { deletePost, fetchPosts, type Post } from '../api/posts'
import { getToken } from '../api/auth'

const posts = ref<Post[]>([])
const loading = ref(true)
const error = ref('')
const isLoggedIn = computed(() => Boolean(getToken()))

onMounted(async () => {
  try {
    posts.value = await fetchPosts()
  } catch {
    error.value = '加载失败，请确认后端正在运行'
  } finally {
    loading.value = false
  }
})

async function handleDelete(id: number) {
  if (!confirm('确定删除这篇文章吗？')) return
  await deletePost(id)
  posts.value = posts.value.filter((post) => post.id !== id)
}
</script>

<template>
  <main>
    <div class="page-head">
      <h1>我的 Agent 博客</h1>
      <router-link v-if="isLoggedIn" to="/new" class="write-btn">＋ 写文章</router-link>
    </div>

    <p v-if="loading">加载中...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <article v-for="post in posts" :key="post.id" class="post-card">
      <h2>{{ post.title }}</h2>
      <p><MarkdownRenderer :content="post.content" /></p>
      <div class="post-meta">
        <small>#{{ post.id }} · {{ post.created_at }}</small>
        <button v-if="isLoggedIn" class="delete-btn" @click="handleDelete(post.id)">删除</button>
      </div>
    </article>
  </main>
</template>

<style scoped>
main {
  max-width: 720px;
  margin: 0 auto;
  padding: 24px;
}
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.write-btn {
  display: inline-block;
  padding: 8px 14px;
  background: #0070f3;
  color: white;
  border-radius: 6px;
  text-decoration: none;
}
.post-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}
.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.delete-btn {
  border: 1px solid #d33;
  color: #d33;
  background: white;
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
}
.error {
  color: red;
}
</style>