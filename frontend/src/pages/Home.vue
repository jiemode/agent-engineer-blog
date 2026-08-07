<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
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

const brickColors = ['red', 'blue', 'green', 'yellow'] as const

function brickClass(id: number) {
  return brickColors[id % brickColors.length]
}
</script>

<template>
  <main class="page-shell home">
    <section class="hero brick-band">
      <div class="hero-copy">
        <h1>Agent Engineer Blog</h1>
        <p>把每一次学习，都搭成一块砖。</p>
        <div class="hero-actions">
          <router-link to="/assistant" class="brick-btn brick-btn--purple">
            AI 助理
          </router-link>
          <router-link v-if="isLoggedIn" to="/new" class="brick-btn brick-btn--red">
            写文章
          </router-link>
          <router-link v-else to="/login" class="brick-btn brick-btn--red">
            登录
          </router-link>
        </div>
      </div>
      <div class="hero-build" aria-hidden="true">
        <span class="big-stud big-stud--red"></span>
        <span class="big-stud big-stud--blue"></span>
        <span class="big-stud big-stud--green"></span>
        <span class="big-stud big-stud--white"></span>
      </div>
    </section>

    <section class="posts-section" aria-label="文章列表">
      <h2>搭建记录</h2>

      <p v-if="loading" class="state-text">加载中...</p>
      <p v-if="error" class="state-text state-text--error">{{ error }}</p>
      <p v-if="!loading && !error && posts.length === 0" class="state-text">
        还没有文章，搭第一块砖吧。
      </p>

      <article
        v-for="post in posts"
        :key="post.id"
        class="post-card brick-band"
        :class="`post-card--${brickClass(post.id)}`"
      >
        <div class="post-card__bar" aria-hidden="true"></div>
        <div class="post-card__body">
          <h3>{{ post.title }}</h3>
          <MarkdownRenderer :content="post.content" />
          <div class="post-card__meta">
            <span>#{{ post.id }} · {{ post.created_at }}</span>
            <button
              v-if="isLoggedIn"
              class="brick-btn brick-btn--ghost brick-btn--small"
              @click="handleDelete(post.id)"
            >
              删除
            </button>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.home {
  padding-top: 28px;
  padding-bottom: 56px;
}

.hero {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 28px;
  align-items: center;
  padding: 32px;
  background: var(--yellow);
}

.hero-copy h1 {
  margin: 0 0 10px;
  font-size: clamp(30px, 5vw, 54px);
  line-height: 1.05;
}

.hero-copy p {
  margin: 0 0 22px;
  font-size: 17px;
  font-weight: 600;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-build {
  display: grid;
  grid-template-columns: repeat(2, 42px);
  gap: 8px;
}

.big-stud {
  width: 42px;
  height: 42px;
  border: 3px solid var(--ink);
  border-radius: 8px;
  box-shadow:
    inset 4px 4px 0 rgba(255, 255, 255, 0.5),
    inset -4px -4px 0 rgba(0, 0, 0, 0.14);
}

.big-stud--red {
  background: var(--red);
}

.big-stud--blue {
  background: var(--blue);
}

.big-stud--green {
  background: var(--green);
}

.big-stud--white {
  background: var(--paper);
}

.posts-section {
  margin-top: 40px;
}

.posts-section h2 {
  margin: 0 0 4px;
  font-size: 22px;
}

.post-card {
  margin-top: 18px;
  overflow: hidden;
  background: #fff;
}

.post-card__bar {
  height: 14px;
  border-bottom: 2px solid var(--ink);
}

.post-card--red .post-card__bar {
  background: var(--red);
}

.post-card--blue .post-card__bar {
  background: var(--blue);
}

.post-card--green .post-card__bar {
  background: var(--green);
}

.post-card--yellow .post-card__bar {
  background: var(--yellow);
}

.post-card__body {
  padding: 18px 20px 20px;
}

.post-card__body h3 {
  margin: 0 0 8px;
  font-size: 21px;
}

.post-card__meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
}

.state-text {
  margin-top: 20px;
  color: var(--muted);
  font-weight: 700;
}

.state-text--error {
  color: var(--red);
}

@media (max-width: 640px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 22px;
  }

  .hero-build {
    display: none;
  }
}
</style>
