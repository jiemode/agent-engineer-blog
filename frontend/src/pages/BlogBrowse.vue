<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowRight,
  FileText,
  LayoutGrid,
  LibraryBig,
  Search,
  Tags,
} from '@lucide/vue'
import { fetchPosts, type Post } from '../api/posts'
import { buildCategories, filterPosts, splitTags } from '../utils/posts'

const route = useRoute()
const router = useRouter()

const posts = ref<Post[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const selectedCategory = ref('')

const categories = computed(() => buildCategories(posts.value))

const areas = computed(() => {
  const counts = new Map<string, { label: string; count: number }>()
  const tones = ['red', 'blue', 'green', 'yellow', 'purple'] as const
  for (const post of posts.value) {
    for (const tag of splitTags(post.tags)) {
      if (!tag.includes('/')) continue
      const parts = tag.split('/').filter(Boolean)
      const label = parts
        .slice(-2)
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(' / ')
      const current = counts.get(tag) ?? { label, count: 0 }
      current.count += 1
      counts.set(tag, current)
    }
  }
  return Array.from(counts.entries()).map(([tag, item], index) => ({
    tag,
    label: item.label,
    count: item.count,
    tone: tones[index % tones.length],
  }))
})

const filteredPosts = computed(() =>
  filterPosts(posts.value, {
    search: search.value,
    category: selectedCategory.value,
  }),
)

function syncTagFromRoute() {
  selectedCategory.value =
    typeof route.query.tag === 'string' ? route.query.tag : ''
}

function updateRouteTag(tag: string) {
  router.replace({ query: tag ? { tag } : {} })
}

function toggleCategory(name: string) {
  selectedCategory.value = selectedCategory.value === name ? '' : name
  updateRouteTag(selectedCategory.value)
}

function selectArea(tag: string) {
  selectedCategory.value = tag
  updateRouteTag(tag)
}

function openPost(post: Post) {
  router.push({
    path: `/post/${post.id}`,
    query: selectedCategory.value ? { tag: selectedCategory.value } : {},
  })
}

function snippetOf(post: Post) {
  return post.content
    .replace(/[#*`>_]/g, '')
    .replace(/\s+/g, ' ')
    .slice(0, 120)
}

watch(() => route.query.tag, syncTagFromRoute)

onMounted(async () => {
  syncTagFromRoute()
  try {
    posts.value = await fetchPosts()
  } catch {
    error.value = '加载失败，请确认后端正在运行'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="browse-page page-shell">
    <div class="browse-layout">
      <aside class="browse-sidebar">
        <div class="sidebar-title">
          <LibraryBig :size="18" />
          <span>书房</span>
        </div>

        <label class="search-box">
          <Search :size="16" />
          <input v-model="search" placeholder="搜索文章标题或正文" />
        </label>

        <button
          type="button"
          class="sidebar-link"
          :class="{ 'is-active': !selectedCategory }"
          @click="toggleCategory('')"
        >
          <LayoutGrid :size="16" />
          <span>全部文章</span>
          <b>{{ posts.length }}</b>
        </button>

        <section class="sidebar-group">
          <p class="sidebar-label">分类</p>
          <button
            v-for="category in categories"
            :key="category.name"
            type="button"
            class="sidebar-link"
            :class="{ 'is-active': selectedCategory === category.name }"
            @click="toggleCategory(category.name)"
          >
            <Tags :size="15" />
            <span>{{ category.name }}</span>
            <b>{{ category.count }}</b>
          </button>
        </section>

        <section v-if="areas.length" class="sidebar-group">
          <p class="sidebar-label">领域</p>
          <button
            v-for="area in areas"
            :key="area.tag"
            type="button"
            :class="['area-link', `area-link--${area.tone}`]"
            @click="selectArea(area.tag)"
          >
            <span>{{ area.label }}</span>
            <b>{{ area.count }}</b>
          </button>
        </section>
      </aside>

      <section class="browse-main">
        <header class="browse-head">
          <div>
            <p class="section-kicker">KNOWLEDGE LIBRARY</p>
            <h1>书房</h1>
            <p class="browse-count">{{ filteredPosts.length }} 篇文章</p>
          </div>
          <div class="mobile-categories">
            <button
              v-for="category in categories"
              :key="category.name"
              type="button"
              class="mobile-chip"
              :class="{ 'is-active': selectedCategory === category.name }"
              @click="toggleCategory(category.name)"
            >
              {{ category.name }}
            </button>
          </div>
        </header>

        <p v-if="loading" class="state-text">加载中...</p>
        <p v-else-if="error" class="state-text state-text--error">{{ error }}</p>
        <p v-else-if="filteredPosts.length === 0" class="state-text">
          没有匹配的文章。
        </p>

        <div v-else class="post-card-grid">
          <article
            v-for="(post, index) in filteredPosts"
            :key="post.id"
            class="post-card"
            :class="`post-card--${['red', 'blue', 'green', 'yellow', 'purple'][index % 5]}`"
            role="button"
            tabindex="0"
            @click="openPost(post)"
            @keydown.enter="openPost(post)"
          >
            <div class="post-card-top">
              <span class="post-number">
                {{ String(index + 1).padStart(2, '0') }}
              </span>
              <span class="post-tags">{{ post.tags || 'UNTAGGED' }}</span>
            </div>
            <FileText class="post-card-icon" :size="20" />
            <h2>{{ post.title }}</h2>
            <p>{{ snippetOf(post) }}</p>
            <div class="post-card-meta">
              <span>#{{ post.id }}</span>
              <span>{{ post.created_at }}</span>
              <span class="read-link">
                阅读
                <ArrowRight :size="14" />
              </span>
            </div>
          </article>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.browse-page {
  padding-top: 28px;
  padding-bottom: 64px;
}

.browse-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 28px;
  align-items: start;
}

.browse-sidebar {
  position: sticky;
  top: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow-sm);
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 20px;
  font-weight: 900;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 11px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: var(--paper);
}

.search-box input {
  min-width: 0;
  padding: 0;
  border: 0;
  background: transparent;
}

.search-box input:focus-visible {
  outline: none;
}

.sidebar-link,
.area-link {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  min-height: 38px;
  padding: 8px 10px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: var(--paper);
  box-shadow: var(--shadow-sm);
  font-size: 13px;
  font-weight: 800;
  text-align: left;
  cursor: pointer;
}

.sidebar-link b,
.area-link b {
  margin-left: auto;
  font-size: 12px;
}

.sidebar-link.is-active {
  background: var(--yellow);
  transform: translate(1px, 1px);
  box-shadow: 0 0 0 var(--ink);
}

.sidebar-group {
  display: grid;
  gap: 8px;
  padding-top: 4px;
}

.sidebar-label {
  margin: 0;
  color: var(--muted);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.05em;
}

.area-link--red { background: var(--red); color: #fff; }
.area-link--blue { background: var(--blue); color: #fff; }
.area-link--green { background: var(--green); color: #fff; }
.area-link--yellow { background: var(--yellow); }
.area-link--purple { background: var(--purple); color: #fff; }

.browse-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 22px;
}

.browse-head h1 {
  margin: 0 0 6px;
  font-size: clamp(32px, 5vw, 52px);
  line-height: 1;
}

.browse-count {
  margin: 0;
  color: var(--muted);
  font-weight: 700;
}

.mobile-categories {
  display: none;
  flex-wrap: wrap;
  gap: 8px;
}

.mobile-chip {
  min-height: 32px;
  padding: 6px 10px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: #fff;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}

.mobile-chip.is-active {
  background: var(--yellow);
}

.post-card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.post-card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 220px;
  padding: 18px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  overflow: hidden;
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease;
}

.post-card::before {
  content: "";
  position: absolute;
  inset: -40%;
  background: radial-gradient(
    circle at 28% 26%,
    rgba(255, 255, 255, 0.45) 0 12%,
    transparent 46%
  );
  opacity: 0;
  transition: opacity 0.18s ease;
  pointer-events: none;
}

.post-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow);
}

.post-card:hover::before {
  opacity: 1;
}

.post-card--red { background: var(--red); color: #fff; }
.post-card--blue { background: var(--blue); color: #fff; }
.post-card--green { background: var(--green); color: #fff; }
.post-card--yellow { background: var(--yellow); }
.post-card--purple { background: var(--purple); color: #fff; }

.post-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 14px;
}

.post-number {
  font-size: 30px;
  font-weight: 900;
  line-height: 1;
  opacity: 0.9;
}

.post-tags {
  max-width: 62%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 10px;
  font-weight: 900;
  opacity: 0.85;
}

.post-card-icon {
  margin-bottom: 12px;
  opacity: 0.85;
}

.post-card h2 {
  margin: 0 0 8px;
  font-size: 22px;
  line-height: 1.12;
}

.post-card > p {
  margin: 0 0 14px;
  font-size: 13px;
  line-height: 1.55;
  opacity: 0.9;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: auto;
  font-size: 11px;
  font-weight: 800;
  opacity: 0.85;
}

.read-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-left: auto;
  font-size: 12px;
  font-weight: 900;
}

.state-text {
  margin-top: 30px;
  color: var(--muted);
  font-weight: 700;
}

.state-text--error {
  color: var(--red);
}

@media (max-width: 900px) {
  .browse-layout {
    grid-template-columns: 1fr;
  }

  .browse-sidebar {
    position: static;
  }

  .sidebar-group {
    display: none;
  }

  .mobile-categories {
    display: flex;
  }
}

@media (max-width: 640px) {
  .post-card-grid {
    grid-template-columns: 1fr;
  }

  .browse-head {
    flex-direction: column;
  }
}
</style>
