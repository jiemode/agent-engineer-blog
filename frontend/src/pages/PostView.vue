<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import {
  ArrowLeft,
  ArrowRight,
  Calendar,
  Sparkles,
  Tags,
  Trash2,
} from '@lucide/vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import {
  deletePost,
  fetchPost,
  fetchPosts,
  type Post,
} from '../api/posts'
import { getToken } from '../api/auth'
import { getRelatedPosts } from '../utils/posts'

const route = useRoute()
const router = useRouter()

const post = ref<Post | null>(null)
const related = ref<Post[]>([])
const loading = ref(true)
const error = ref('')
const notFound = ref(false)
const isLoggedIn = computed(() => Boolean(getToken()))
const tag = computed(() =>
  typeof route.query.tag === 'string' ? route.query.tag : '',
)
const querySearch = computed(() =>
  typeof route.query.q === 'string' ? route.query.q : '',
)
const postId = computed(() => Number(route.params.id))

async function load() {
  loading.value = true
  error.value = ''
  notFound.value = false
  post.value = null
  related.value = []

  const id = postId.value
  if (!Number.isInteger(id) || id <= 0) {
    notFound.value = true
    loading.value = false
    return
  }

  try {
    post.value = await fetchPost(id)
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      notFound.value = true
    } else {
      error.value = '加载失败，请确认后端正在运行'
    }
  }

  if (post.value) {
    try {
      const all = await fetchPosts()
      related.value = getRelatedPosts(all, post.value, 3)
    } catch {
      related.value = []
    }
  }

  loading.value = false
}

function backToBrowse() {
  const query: Record<string, string> = {}
  if (tag.value) query.tag = tag.value
  if (querySearch.value) query.q = querySearch.value
  router.push({
    path: '/browse',
    query,
  })
}

async function handleDelete() {
  if (!post.value || !confirm('确定删除这篇文章吗？')) return
  try {
    await deletePost(post.value.id)
    router.push('/browse')
  } catch {
    error.value = '删除失败'
  }
}

watch(postId, load)
onMounted(load)
</script>

<template>
  <main class="post-page page-shell">
    <div class="post-toolbar">
      <button type="button" class="back-link" @click="backToBrowse">
        <ArrowLeft :size="16" />
        返回书房
      </button>
      <span v-if="tag" class="tag-chip">
        <Tags :size="14" />
        {{ tag }}
      </span>
    </div>

    <p v-if="loading" class="state-text">加载中...</p>
    <p v-else-if="error" class="state-text state-text--error">{{ error }}</p>
    <p v-else-if="notFound" class="state-text">文章不存在或已被删除。</p>

    <article v-else-if="post" class="post-article">
      <header class="post-header">
        <p class="section-kicker">READING LOG</p>
        <h1>{{ post.title }}</h1>
        <div class="post-meta">
          <span>
            <Calendar :size="14" />
            {{ post.created_at }}
          </span>
          <span>#{{ post.id }}</span>
          <span>
            <Tags :size="14" />
            {{ post.tags || 'UNTAGGED' }}
          </span>
          <button
            v-if="isLoggedIn"
            type="button"
            class="delete-link"
            @click="handleDelete"
          >
            <Trash2 :size="14" />
            删除
          </button>
        </div>
      </header>

      <MarkdownRenderer :content="post.content" />
    </article>

    <section v-if="related.length" class="related-section">
      <div class="related-head">
        <p class="section-kicker">KEEP READING</p>
        <h2>继续读</h2>
      </div>
      <div class="related-grid">
        <router-link
          v-for="item in related"
          :key="item.id"
          :to="{
            path: `/post/${item.id}`,
            query: {
              ...(tag ? { tag } : {}),
              ...(querySearch ? { q: querySearch } : {}),
            },
          }"
          class="related-card"
        >
          <span>
            <Sparkles :size="16" />
            {{ item.title }}
          </span>
          <ArrowRight :size="15" />
        </router-link>
      </div>
    </section>
  </main>
</template>

<style scoped>
.post-page {
  padding-top: 24px;
  padding-bottom: 64px;
}

.post-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  margin-bottom: 26px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 12px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow-sm);
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 11px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: var(--yellow);
  box-shadow: var(--shadow-sm);
  font-size: 12px;
  font-weight: 900;
}

.post-article {
  max-width: 860px;
  padding-bottom: 36px;
  border-bottom: 2px solid var(--ink);
}

.post-header {
  margin-bottom: 28px;
}

.post-header h1 {
  margin: 0 0 14px;
  font-size: clamp(34px, 6vw, 62px);
  line-height: 1.05;
}

.post-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.post-meta span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.delete-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  padding: 7px 11px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: var(--red);
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.related-section {
  padding-top: 32px;
}

.related-head h2 {
  margin: 0 0 16px;
  font-size: 28px;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.related-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 96px;
  padding: 16px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow-sm);
  color: var(--ink);
  text-decoration: none;
  font-size: 14px;
  font-weight: 900;
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease;
}

.related-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow);
}

.related-card span {
  display: inline-flex;
  align-items: center;
  gap: 9px;
}

.state-text {
  margin-top: 30px;
  color: var(--muted);
  font-weight: 700;
}

.state-text--error {
  color: var(--red);
}

@media (max-width: 760px) {
  .related-grid {
    grid-template-columns: 1fr;
  }

  .post-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
