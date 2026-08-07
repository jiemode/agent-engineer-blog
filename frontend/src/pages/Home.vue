<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import { deletePost, fetchPosts, type Post } from '../api/posts'
import { getToken } from '../api/auth'

const posts = ref<Post[]>([])
const loading = ref(true)
const error = ref('')
const isLoggedIn = computed(() => Boolean(getToken()))
const selectedCategory = ref('')
const search = ref('')

onMounted(async () => {
  try {
    posts.value = await fetchPosts()
  } catch {
    error.value = '加载失败，请确认后端正在运行'
  } finally {
    loading.value = false
  }
})

const categories = computed(() => {
  const counts = new Map<string, number>()
  for (const post of posts.value) {
    for (const tag of post.tags
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean)) {
      counts.set(tag, (counts.get(tag) ?? 0) + 1)
    }
  }
  return Array.from(counts.entries()).map(([name, count]) => ({ name, count }))
})

const filteredPosts = computed(() => {
  const query = search.value.trim().toLowerCase()
  return posts.value.filter((post) => {
    const matchCategory =
      !selectedCategory.value || post.tags.includes(selectedCategory.value)
    const matchSearch =
      !query ||
      post.title.toLowerCase().includes(query) ||
      post.content.toLowerCase().includes(query)
    return matchCategory && matchSearch
  })
})

const categoryColors = ['red', 'blue', 'green', 'yellow', 'purple'] as const

function categoryColor(index: number) {
  return categoryColors[index % categoryColors.length]
}

function toggleCategory(name: string) {
  selectedCategory.value = selectedCategory.value === name ? '' : name
}

async function handleDelete(id: number) {
  if (!confirm('确定删除这篇文章吗？')) return
  await deletePost(id)
  posts.value = posts.value.filter((post) => post.id !== id)
}
</script>

<template>
  <main>
    <section class="hero page-shell">
      <div class="hero-copy">
        <h1>
          一座可拼装的<br />
          知识世界
        </h1>
        <p>
          {{ posts.length }} 篇文章，每一篇都是一块积木。
          拼一拼，看看一个 Agent 工程师是怎么长出来的。
        </p>
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

      <div class="hero-stage" aria-hidden="true">
        <div class="brick-tile brick-tile--red">
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
        </div>
        <div class="brick-tile brick-tile--blue">
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
        </div>
        <div class="brick-tile brick-tile--green">
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
        </div>
        <div class="brick-tile brick-tile--yellow">
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
        </div>
        <div class="brick-tile brick-tile--purple">
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
          <span class="stud"></span>
        </div>
      </div>
    </section>

    <div class="marquee" aria-hidden="true">
      <div class="marquee-track">
        <span>BUILD</span><span>·</span><span>LEARN</span><span>·</span>
        <span>GROW</span><span>·</span><span>AGENT</span><span>·</span>
        <span>RAG</span><span>·</span><span>BUILD</span><span>·</span>
        <span>LEARN</span><span>·</span><span>GROW</span><span>·</span>
        <span>AGENT</span><span>·</span><span>RAG</span><span>·</span>
      </div>
    </div>

    <section class="page-shell browse">
      <div class="browse-head">
        <h2>按知识域漫游</h2>
        <div class="category-row">
          <button
            v-for="(category, index) in categories"
            :key="category.name"
            :class="[
              'category-brick',
              `category-brick--${categoryColor(index)}`,
              { 'is-active': selectedCategory === category.name },
            ]"
            @click="toggleCategory(category.name)"
          >
            <span class="mini-stud"></span>
            {{ category.name }} · {{ category.count }}
          </button>
        </div>
      </div>

      <div class="search-row">
        <input v-model="search" placeholder="搜索文章标题或正文" />
      </div>

      <p v-if="loading" class="state-text">加载中...</p>
      <p v-if="error" class="state-text state-text--error">{{ error }}</p>
      <p v-if="!loading && !error && filteredPosts.length === 0" class="state-text">
        还没有文章，搭第一块砖吧。
      </p>

      <section aria-label="文章列表">
        <article
          v-for="(post, index) in filteredPosts"
          :key="post.id"
          class="post-row"
        >
          <span class="post-number">{{ String(index + 1).padStart(2, '0') }}</span>
          <div class="post-main">
            <div class="post-titleline">
              <h3>{{ post.title }}</h3>
              <button
                v-if="isLoggedIn"
                class="brick-btn brick-btn--ghost brick-btn--small"
                @click="handleDelete(post.id)"
              >
                删除
              </button>
            </div>
            <div class="post-meta">#{{ post.id }} · {{ post.created_at }}</div>
            <MarkdownRenderer :content="post.content" />
          </div>
        </article>
      </section>
    </section>
  </main>
</template>

<style scoped>
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 420px;
  gap: 40px;
  align-items: center;
  padding-top: 64px;
  padding-bottom: 72px;
}

.hero-copy h1 {
  margin: 0 0 18px;
  max-width: 12ch;
  font-size: clamp(46px, 8vw, 104px);
  line-height: 0.94;
  font-weight: 900;
}

.hero-copy p {
  max-width: 54ch;
  margin: 0 0 26px;
  font-size: 19px;
  line-height: 1.6;
  font-weight: 600;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-stage {
  position: relative;
  min-height: 340px;
}

.brick-tile {
  position: absolute;
  display: grid;
  grid-template-columns: repeat(2, 22px);
  gap: 7px;
  width: 126px;
  height: 84px;
  padding: 14px;
  border: 3px solid var(--ink);
  border-radius: 6px;
  box-shadow:
    inset 3px 3px 0 rgba(255, 255, 255, 0.45),
    inset -3px -3px 0 rgba(0, 0, 0, 0.12),
    var(--shadow);
}

.brick-tile .stud {
  width: 22px;
  height: 22px;
  border: 2px solid var(--ink);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.85);
  box-shadow:
    inset 2px 2px 0 rgba(255, 255, 255, 0.9),
    inset -2px -2px 0 rgba(0, 0, 0, 0.15);
}

.brick-tile--red {
  background: var(--red);
  top: 12px;
  left: 24px;
  transform: rotate(-6deg);
}

.brick-tile--blue {
  background: var(--blue);
  top: 96px;
  left: 150px;
  transform: rotate(4deg);
}

.brick-tile--green {
  background: var(--green);
  top: 176px;
  left: 40px;
  transform: rotate(7deg);
}

.brick-tile--yellow {
  background: var(--yellow);
  top: 44px;
  left: 260px;
  transform: rotate(-3deg);
}

.brick-tile--purple {
  background: var(--purple);
  top: 190px;
  left: 236px;
  transform: rotate(-8deg);
}

.browse {
  padding-top: 56px;
  padding-bottom: 64px;
}

.browse-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 20px;
}

.browse-head h2 {
  margin: 0;
  font-size: 30px;
}

.category-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.category-brick {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  padding: 7px 13px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow-sm);
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  transition:
    transform 0.12s ease,
    box-shadow 0.12s ease;
}

.category-brick:hover {
  transform: translate(-1px, -1px);
  box-shadow: var(--shadow);
}

.category-brick.is-active {
  transform: translate(1px, 1px);
  box-shadow: 0 0 0 var(--ink);
}

.mini-stud {
  width: 12px;
  height: 12px;
  border: 2px solid var(--ink);
  border-radius: 50%;
  background: var(--yellow);
  box-shadow: inset 2px 2px 0 rgba(255, 255, 255, 0.8);
}

.category-brick--red .mini-stud {
  background: var(--red);
}

.category-brick--blue .mini-stud {
  background: var(--blue);
}

.category-brick--green .mini-stud {
  background: var(--green);
}

.category-brick--yellow .mini-stud {
  background: var(--yellow);
}

.category-brick--purple .mini-stud {
  background: var(--purple);
}

.search-row {
  margin-top: 22px;
}

.post-row {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 20px;
  padding: 30px 0;
  border-bottom: 2px solid var(--ink);
}

.post-number {
  font-size: 42px;
  font-weight: 900;
  line-height: 1;
}

.post-titleline {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  flex-wrap: wrap;
}

.post-titleline h3 {
  margin: 0;
  font-size: clamp(22px, 3vw, 32px);
  line-height: 1.15;
}

.post-meta {
  margin: 8px 0 14px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.state-text {
  margin-top: 24px;
  color: var(--muted);
  font-weight: 700;
}

.state-text--error {
  color: var(--red);
}

@media (max-width: 860px) {
  .hero {
    grid-template-columns: 1fr;
    padding-top: 44px;
    padding-bottom: 48px;
  }

  .hero-stage {
    display: none;
  }
}

@media (max-width: 640px) {
  .post-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .post-number {
    font-size: 30px;
  }
}
</style>
