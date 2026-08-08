# Blog 拆分与首页升级 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split article browsing into a dedicated two-column library page and independent article pages, while upgrading the homepage into a lighter, richer visual portal.

**Architecture:** Vue Router gains `/browse` and `/post/:id`. The homepage is trimmed to hero, stats, latest bricks, growth path, and CTA. Shared post filtering/stats logic lives in `src/utils/posts.ts`, and existing FastAPI endpoints are reused through `src/api/posts.ts`.

**Tech Stack:** Vue 3, TypeScript, Vite, Vue Router, Axios, Vitest, @lucide/vue.

---

## File Structure

- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/utils/posts.ts`
- Create: `frontend/src/utils/posts.test.ts`
- Create: `frontend/src/api/posts.test.ts`
- Create: `frontend/src/pages/BlogBrowse.vue`
- Create: `frontend/src/pages/PostView.vue`
- Create: `frontend/src/assets/hero-bricks.jpg`
- Modify: `frontend/package.json`
- Modify: `frontend/src/api/posts.ts`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/pages/Home.vue`
- Modify: `frontend/src/styles/bricks.css`

---

### Task 1: Test Infrastructure and Post Utilities

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/utils/posts.ts`
- Test: `frontend/src/utils/posts.test.ts`

- [ ] **Step 1: Install Vitest**

Run:

```bash
pnpm add -D vitest
```

Expected: package lock updates and `vitest` appears in `frontend/package.json` devDependencies.

- [ ] **Step 2: Add the test script**

In `frontend/package.json`, change scripts to:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run"
  }
}
```

- [ ] **Step 3: Create the Vitest config**

Create `frontend/vitest.config.ts`:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})
```

- [ ] **Step 4: Write the failing tests**

Create `frontend/src/utils/posts.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import type { Post } from '../api/posts'
import {
  buildCategories,
  computeStats,
  filterPosts,
  getLatestPosts,
  getRelatedPosts,
  splitTags,
} from './posts'

const samplePosts: Post[] = [
  {
    id: 1,
    title: 'FastAPI Router',
    content: '# heading\n- item\n```python\nx=1\n```',
    tags: 'fastapi, architecture',
    created_at: '2026-08-01',
  },
  {
    id: 2,
    title: 'Pydantic Models',
    content: 'plain text',
    tags: 'python, fastapi',
    created_at: '2026-08-02',
  },
  {
    id: 3,
    title: 'Git Staging',
    content: 'note',
    tags: 'git',
    created_at: '2026-08-03',
  },
]

describe('post utilities', () => {
  it('splits comma separated tags', () => {
    expect(splitTags(' fastapi , architecture ')).toEqual([
      'fastapi',
      'architecture',
    ])
  })

  it('builds categories with counts', () => {
    const categories = buildCategories(samplePosts)
    expect(categories.find((c) => c.name === 'fastapi')?.count).toBe(2)
    expect(categories).toHaveLength(4)
  })

  it('filters by category and search text', () => {
    expect(filterPosts(samplePosts, { category: 'fastapi' })).toHaveLength(2)
    expect(filterPosts(samplePosts, { search: 'router' })).toHaveLength(1)
  })

  it('returns newest posts first', () => {
    expect(getLatestPosts(samplePosts, 2).map((p) => p.id)).toEqual([3, 2])
  })

  it('computes stats from real content', () => {
    const stats = computeStats(samplePosts)
    expect(stats.posts).toBe(3)
    expect(stats.categories).toBe(4)
    expect(stats.knowledgeBlocks).toBe(4)
    expect(stats.totalChars).toBeGreaterThan(0)
  })

  it('ranks related posts by shared tags', () => {
    expect(getRelatedPosts(samplePosts, samplePosts[0]).map((p) => p.id)).toEqual([
      2,
      3,
    ])
  })
})
```

- [ ] **Step 5: Run tests and verify they fail**

Run:

```bash
pnpm test
```

Expected: FAIL with `Cannot find module '../utils/posts'`.

- [ ] **Step 6: Implement the utilities**

Create `frontend/src/utils/posts.ts`:

```ts
import type { Post } from '../api/posts'

export interface Category {
  name: string
  count: number
}

export interface BlogStats {
  posts: number
  categories: number
  knowledgeBlocks: number
  totalChars: number
}

export function splitTags(tags: string): string[] {
  return tags
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

export function buildCategories(posts: Post[]): Category[] {
  const counts = new Map<string, number>()
  for (const post of posts) {
    for (const tag of splitTags(post.tags)) {
      counts.set(tag, (counts.get(tag) ?? 0) + 1)
    }
  }
  return Array.from(counts.entries()).map(([name, count]) => ({ name, count }))
}

export function filterPosts(
  posts: Post[],
  filters: { search?: string; category?: string } = {},
): Post[] {
  const query = filters.search?.trim().toLowerCase() ?? ''
  const category = filters.category?.trim()
  return posts.filter((post) => {
    const matchCategory = !category || splitTags(post.tags).includes(category)
    const matchSearch =
      !query ||
      post.title.toLowerCase().includes(query) ||
      post.content.toLowerCase().includes(query)
    return matchCategory && matchSearch
  })
}

export function getLatestPosts(posts: Post[], limit: number): Post[] {
  return [...posts].sort((a, b) => b.id - a.id).slice(0, limit)
}

export function computeStats(posts: Post[]): BlogStats {
  let knowledgeBlocks = 0
  let totalChars = 0
  for (const post of posts) {
    const headings = post.content.match(/^#{1,6}\s/gm)?.length ?? 0
    const bullets = post.content.match(/^[-*+]\s/gm)?.length ?? 0
    const fences = post.content.match(/```/g)?.length ?? 0
    knowledgeBlocks += headings + bullets + fences
    totalChars += post.content.length
  }
  return {
    posts: posts.length,
    categories: buildCategories(posts).length,
    knowledgeBlocks,
    totalChars,
  }
}

function relatedScore(post: Post, tags: string[]): number {
  return splitTags(post.tags).filter((tag) => tags.includes(tag)).length
}

export function getRelatedPosts(posts: Post[], post: Post, limit = 3): Post[] {
  const tags = splitTags(post.tags)
  return posts
    .filter((item) => item.id !== post.id)
    .sort((a, b) => relatedScore(b, tags) - relatedScore(a, tags))
    .slice(0, limit)
}
```

- [ ] **Step 7: Run tests and verify they pass**

Run:

```bash
pnpm test
```

Expected: 6 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/package.json frontend/pnpm-lock.yaml frontend/vitest.config.ts frontend/src/utils/posts.ts frontend/src/utils/posts.test.ts
git commit -m "test: add post utilities with vitest"
```

---

### Task 2: Single Post API

**Files:**
- Modify: `frontend/src/api/posts.ts`
- Test: `frontend/src/api/posts.test.ts`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/api/posts.test.ts`:

```ts
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('./http', () => ({ default: { get: vi.fn() } }))

import http from './http'
import { fetchPost } from './posts'

const mockedGet = vi.mocked(http.get)

describe('fetchPost', () => {
  beforeEach(() => {
    mockedGet.mockReset()
  })

  it('requests one post by id', async () => {
    mockedGet.mockResolvedValue({
      data: {
        id: 7,
        title: 'Title',
        content: 'Body',
        tags: 'fastapi',
        created_at: '2026-08-08',
      },
    })

    const post = await fetchPost(7)

    expect(mockedGet).toHaveBeenCalledWith('/posts/7')
    expect(post.title).toBe('Title')
  })
})
```

- [ ] **Step 2: Run test and verify it fails**

Run:

```bash
pnpm test src/api/posts.test.ts
```

Expected: FAIL with `fetchPost is not a function`.

- [ ] **Step 3: Implement fetchPost**

In `frontend/src/api/posts.ts`, add below `fetchPosts`:

```ts
export async function fetchPost(id: number | string): Promise<Post> {
  const { data } = await http.get<Post>(`/posts/${id}`)
  return data
}
```

- [ ] **Step 4: Run test and verify it passes**

Run:

```bash
pnpm test src/api/posts.test.ts
```

Expected: 1 test PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/posts.ts frontend/src/api/posts.test.ts
git commit -m "feat: add fetchPost api"
```

---

### Task 3: Routes, Icons, and Navigation Shell

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/src/router/index.ts`
- Create: `frontend/src/pages/BlogBrowse.vue`
- Create: `frontend/src/pages/PostView.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Install @lucide/vue**

Run:

```bash
pnpm add @lucide/vue
```

Expected: package lock updates and `@lucide/vue` appears in dependencies.

- [ ] **Step 2: Create route placeholder pages**

Create `frontend/src/pages/BlogBrowse.vue`:

```vue
<template>
  <main class="page-shell">
    <h1>书房</h1>
    <p>加载中...</p>
  </main>
</template>
```

Create `frontend/src/pages/PostView.vue`:

```vue
<template>
  <main class="page-shell">
    <p>加载文章...</p>
  </main>
</template>
```

- [ ] **Step 3: Register routes**

Replace `frontend/src/router/index.ts` with:

```ts
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Login from '../pages/Login.vue'
import NewPost from '../pages/NewPost.vue'
import Assistant from '../pages/Assistant.vue'
import BlogBrowse from '../pages/BlogBrowse.vue'
import PostView from '../pages/PostView.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/browse', component: BlogBrowse },
  { path: '/post/:id', component: PostView },
  { path: '/login', component: Login },
  { path: '/new', component: NewPost },
  { path: '/assistant', component: Assistant },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  if (to.path === '/new' && !localStorage.getItem('access_token')) {
    return '/login'
  }
})

export default router
```

- [ ] **Step 4: Update App navigation**

In `frontend/src/App.vue`, replace the `<nav class="header-nav">` block with:

```html
<nav class="header-nav" aria-label="主导航">
  <router-link to="/browse" class="nav-link">书房</router-link>
  <router-link to="/assistant" class="nav-link">AI 助理</router-link>
  <router-link v-if="isLoggedIn" to="/new" class="brick-btn brick-btn--red">
    写文章
  </router-link>
  <router-link v-else to="/login" class="brick-btn brick-btn--red">
    登录
  </router-link>
  <button v-if="isLoggedIn" class="nav-link nav-link--button" @click="logout">
    退出
  </button>
</nav>
```

In `frontend/src/App.vue`, replace the footer links block with:

```html
<div class="footer-links">
  <router-link to="/">首页</router-link>
  <router-link to="/browse">书房</router-link>
  <router-link to="/assistant">问笔记</router-link>
</div>
```

- [ ] **Step 5: Verify TypeScript build still passes**

Run:

```bash
pnpm build
```

Expected: build succeeds.

- [ ] **Step 6: Commit**

```bash
git add frontend/package.json frontend/pnpm-lock.yaml frontend/src/router/index.ts frontend/src/pages/BlogBrowse.vue frontend/src/pages/PostView.vue frontend/src/App.vue
git commit -m "feat: add browse and post routes"
```

---

### Task 4: BlogBrowse Page

**Files:**
- Modify: `frontend/src/pages/BlogBrowse.vue`

- [ ] **Step 1: Replace the placeholder with the full library page**

Replace `frontend/src/pages/BlogBrowse.vue` with:

```vue
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
            @click="openPost(post)"
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
```

- [ ] **Step 2: Run build and verify it passes**

Run:

```bash
pnpm build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/BlogBrowse.vue
git commit -m "feat: build two-column blog library page"
```

---

### Task 5: PostView Page

**Files:**
- Modify: `frontend/src/pages/PostView.vue`

- [ ] **Step 1: Replace the placeholder with the full article page**

Replace `frontend/src/pages/PostView.vue` with:

```vue
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
    const all = await fetchPosts()
    related.value = getRelatedPosts(all, post.value, 3)
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      notFound.value = true
    } else {
      error.value = '加载失败，请确认后端正在运行'
    }
  } finally {
    loading.value = false
  }
}

function backToBrowse() {
  router.push({
    path: '/browse',
    query: tag.value ? { tag: tag.value } : {},
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
            query: tag.value ? { tag: tag.value } : {},
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
```

- [ ] **Step 2: Run build and verify it passes**

Run:

```bash
pnpm build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/PostView.vue
git commit -m "feat: build independent article page"
```

---

### Task 6: Hero Image Asset

**Files:**
- Create: `frontend/src/assets/hero-bricks.jpg`

- [ ] **Step 1: Generate the hero image**

Invoke the `imagegen` skill and generate a 1920x1080 bitmap named `hero-bricks.jpg` with this prompt:

```text
Colorful LEGO-style bricks and AI engineering tools arranged like an abstract knowledge city, bright red blue yellow green purple palette, crisp studio lighting, no text, no watermark.
```

Save the output to `frontend/src/assets/hero-bricks.jpg`.

- [ ] **Step 2: Fallback if generation is unavailable**

If image generation cannot run, copy the existing asset instead:

```bash
Copy-Item frontend/src/assets/lego-pile.jpg frontend/src/assets/hero-bricks.jpg
```

Expected: `frontend/src/assets/hero-bricks.jpg` exists.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/assets/hero-bricks.jpg
git commit -m "feat: add hero image asset"
```

---

### Task 7: Homepage Redesign

**Files:**
- Modify: `frontend/src/pages/Home.vue`
- Modify: `frontend/src/styles/bricks.css`

- [ ] **Step 1: Add shared visual utilities**

Append to `frontend/src/styles/bricks.css`:

```css
.grid-bg {
  background-image:
    linear-gradient(90deg, rgba(16, 16, 16, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(16, 16, 16, 0.08) 1px, transparent 1px);
  background-size: 28px 28px;
}

.spotlight-card {
  position: relative;
  overflow: hidden;
}

.spotlight-card::before {
  content: "";
  position: absolute;
  inset: -40%;
  background: radial-gradient(
    circle at 30% 30%,
    rgba(255, 255, 255, 0.45) 0 10%,
    transparent 46%
  );
  opacity: 0;
  transition: opacity 0.18s ease;
  pointer-events: none;
}

.spotlight-card:hover::before {
  opacity: 1;
}
```

- [ ] **Step 2: Replace Home.vue**

Replace `frontend/src/pages/Home.vue` with:

```vue
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ArrowRight,
  LibraryBig,
  MessageCircle,
  Sparkles,
} from '@lucide/vue'
import { fetchPosts, type Post } from '../api/posts'
import { computeStats, getLatestPosts } from '../utils/posts'
import heroBricks from '../assets/hero-bricks.jpg'
import legoPile from '../assets/lego-pile.jpg'
import legoFrozen from '../assets/lego-frozen.jpg'
import legoDuplo from '../assets/lego-duplo.jpg'

const posts = ref<Post[]>([])
const loading = ref(true)
const error = ref('')

const stats = computed(() => computeStats(posts.value))
const latestPosts = computed(() => getLatestPosts(posts.value, 6))
const cardImages = [legoPile, legoFrozen, legoDuplo, heroBricks]
const categoryColors = ['red', 'blue', 'green', 'yellow', 'purple'] as const

const journey = [
  {
    step: 'STEP 01',
    title: '看懂一次请求',
    text: '从 FastAPI 的 Schema、Router、Service 开始，理解谁负责接客、谁负责干活。',
    color: 'red',
  },
  {
    step: 'STEP 02',
    title: '让知识可检索',
    text: '把笔记变成可查询的知识库，让 AI 的回答有据可依，形成 RAG 的闭环。',
    color: 'blue',
  },
  {
    step: 'STEP 03',
    title: '做出活的 Agent',
    text: '接入流式输出、上下文记忆和工具调用，把“能聊天”升级成“能办事”。',
    color: 'yellow',
  },
  {
    step: 'STEP 04',
    title: '上线并持续迭代',
    text: '前端交给 GitHub Pages，API 交给 Render，数据交给 Postgres。每次提交都是发布。',
    color: 'green',
  },
]

onMounted(async () => {
  try {
    posts.value = await fetchPosts()
  } catch {
    error.value = '加载失败，请确认后端正在运行'
  } finally {
    loading.value = false
  }
})

function categoryColor(index: number) {
  return categoryColors[index % categoryColors.length]
}

function snippetOf(post: Post) {
  return post.content
    .replace(/[#*`>_]/g, '')
    .replace(/\s+/g, ' ')
    .slice(0, 110)
}
</script>

<template>
  <main class="home">
    <section class="hero">
      <img
        class="hero-photo"
        :src="heroBricks"
        alt="彩色积木构成的 AI 知识城市"
      />
      <div class="hero-veil" aria-hidden="true"></div>
      <div class="hero-grid" aria-hidden="true"></div>

      <div class="hero-inner page-shell">
        <p class="eyebrow">
          <span class="live-dot"></span>
          A BLOG BUILT LIKE A BRICK SET
        </p>
        <h1>一座可拼接的<br />知识世界</h1>
        <p class="hero-lead">
          从零开始做 AI Agent 的完整旅程：写接口、建知识库、训练助理、部署上线。
          每篇文章都是一块积木，随时可以拆开、重组、复用。
        </p>
        <div class="hero-actions">
          <router-link to="/browse" class="brick-btn brick-btn--yellow">
            <LibraryBig :size="18" />
            浏览文章
          </router-link>
          <router-link to="/assistant" class="brick-btn brick-btn--ghost">
            <MessageCircle :size="18" />
            问我的笔记
          </router-link>
        </div>
      </div>
    </section>

    <div class="marquee" aria-hidden="true">
      <div class="marquee-track">
        <span>BUILD</span><span>路</span><span>LEARN</span><span>路</span>
        <span>GROW</span><span>路</span><span>AGENT</span><span>路</span>
        <span>RAG</span><span>路</span><span>DEPLOY</span><span>路</span>
        <span>BUILD</span><span>路</span><span>LEARN</span><span>路</span>
        <span>GROW</span><span>路</span><span>AGENT</span><span>路</span>
        <span>RAG</span><span>路</span><span>DEPLOY</span><span>路</span>
      </div>
    </div>

    <section class="stats-strip page-shell" aria-label="博客数据统计">
      <div
        v-for="(stat, index) in [
          { label: '文章', value: stats.posts, tone: 'red' },
          { label: '分类', value: stats.categories, tone: 'blue' },
          { label: '知识块', value: stats.knowledgeBlocks, tone: 'yellow' },
          { label: '总字数', value: stats.totalChars, tone: 'green' },
        ]"
        :key="stat.label"
        :class="['stat-brick', `stat-brick--${stat.tone}`]"
      >
        <span class="stat-value">{{ stat.value.toLocaleString() }}</span>
        <span class="stat-label">{{ stat.label }}</span>
      </div>
    </section>

    <section class="latest-section page-shell" aria-label="最近精选">
      <div class="section-head section-head--left">
        <p class="section-kicker">LATEST BRICKS</p>
        <h2>最近精选</h2>
        <p>最新拼上的几块知识积木，点进去进入独立文章页。</p>
      </div>

      <p v-if="loading" class="state-text">加载中...</p>
      <p v-else-if="error" class="state-text state-text--error">{{ error }}</p>
      <p v-else-if="latestPosts.length === 0" class="state-text">
        还没有文章，等第一块积木出现。
      </p>

      <div v-else class="latest-grid">
        <router-link
          v-for="(post, index) in latestPosts"
          :key="post.id"
          :to="{ path: `/post/${post.id}` }"
          :class="['latest-card', `latest-card--${categoryColor(index)}`]"
        >
          <div class="latest-card-top">
            <span class="latest-number">
              {{ String(post.id).padStart(2, '0') }}
            </span>
            <span class="latest-tags">{{ post.tags || 'UNTAGGED' }}</span>
          </div>
          <img
            class="latest-photo"
            :src="cardImages[index % cardImages.length]"
            alt="彩色积木"
          />
          <h3>{{ post.title }}</h3>
          <p>{{ snippetOf(post) }}</p>
          <span class="latest-meta">
            {{ post.created_at }}
            <ArrowRight :size="14" />
          </span>
        </router-link>
      </div>
    </section>

    <section class="journey-section page-shell">
      <div class="journey-head">
        <p class="section-kicker">LEARNING PATH</p>
        <h2>从 0 到 1 的成长路线</h2>
        <p>每一步都在真实项目里发生过：踩坑、复盘、写进博客、变成能力。</p>
      </div>

      <ol class="journey-list">
        <li
          v-for="item in journey"
          :key="item.step"
          class="journey-item"
        >
          <span :class="['journey-step', `journey-step--${item.color}`]">
            {{ item.step }}
          </span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </li>
        <li class="journey-item journey-item--ai">
          <span class="journey-step journey-step--purple">
            <Sparkles :size="14" />
            AI 评测
          </span>
          <h3>能力评测即将上线</h3>
          <p>根据成长路线生成测评题，看看你目前处于哪一级。</p>
          <span class="coming-soon">COMING SOON</span>
        </li>
      </ol>
    </section>

    <section class="cta-section">
      <div class="cta-inner page-shell grid-bg">
        <p class="section-kicker">TRY THE ASSISTANT</p>
        <h2>把笔记交给 Agent</h2>
        <p>用自然语言提问，AI 会从这些博客里找出答案和出处。</p>
        <router-link to="/assistant" class="brick-btn brick-btn--yellow">
          <MessageCircle :size="18" />
          开始提问
        </router-link>
      </div>
    </section>
  </main>
</template>

<style scoped>
.hero {
  position: relative;
  min-height: 82svh;
  display: flex;
  align-items: center;
  overflow: hidden;
  border-bottom: 3px solid var(--ink);
}

.hero-photo {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 42%;
}

.hero-veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(16, 16, 16, 0.78) 0%, rgba(16, 16, 16, 0.48) 58%, rgba(16, 16, 16, 0.18) 100%),
    linear-gradient(0deg, rgba(16, 16, 16, 0.55) 0%, transparent 42%);
}

.hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(255, 255, 255, 0.08) 1px, transparent 1px);
  background-size: 34px 34px;
  pointer-events: none;
}

.hero-inner {
  position: relative;
  z-index: 1;
  width: 100%;
  padding-top: 72px;
  padding-bottom: 72px;
  color: #fff;
}

.eyebrow,
.section-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 14px;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.eyebrow {
  padding: 6px 10px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: var(--yellow);
  color: var(--ink);
  box-shadow: var(--shadow-sm);
}

.live-dot {
  width: 9px;
  height: 9px;
  border: 2px solid var(--ink);
  border-radius: 50%;
  background: var(--green);
  animation: live-pulse 1.6s ease-in-out infinite;
}

.hero-inner h1 {
  max-width: 9ch;
  margin: 0 0 22px;
  font-size: clamp(52px, 9vw, 118px);
  line-height: 0.93;
  font-weight: 900;
  text-shadow: 4px 4px 0 rgba(16, 16, 16, 0.65);
}

.hero-lead {
  max-width: 58ch;
  margin: 0 0 28px;
  font-size: 19px;
  line-height: 1.65;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.92);
  text-shadow: 2px 2px 0 rgba(16, 16, 16, 0.5);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-actions .brick-btn {
  gap: 8px;
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  padding-top: 28px;
  padding-bottom: 28px;
}

.stat-brick {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 118px;
  padding: 18px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.stat-value {
  font-size: clamp(26px, 4vw, 42px);
  font-weight: 900;
  line-height: 1;
}

.stat-label {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 800;
  opacity: 0.85;
}

.stat-brick--red { background: var(--red); color: #fff; }
.stat-brick--blue { background: var(--blue); color: #fff; }
.stat-brick--yellow { background: var(--yellow); }
.stat-brick--green { background: var(--green); color: #fff; }

.latest-section,
.journey-section {
  padding-top: 56px;
  padding-bottom: 64px;
}

.section-head {
  max-width: 620px;
  margin-bottom: 30px;
}

.section-head--left {
  margin-left: 0;
}

.section-head h2,
.journey-head h2,
.cta-inner h2 {
  margin: 0 0 14px;
  font-size: clamp(30px, 4vw, 46px);
  line-height: 1.04;
}

.section-head > p:not(.section-kicker),
.journey-head > p:not(.section-kicker),
.cta-inner > p:not(.section-kicker) {
  margin: 0;
  color: var(--muted);
  font-size: 16px;
  line-height: 1.7;
  font-weight: 600;
}

.latest-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.latest-card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 310px;
  padding: 18px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  color: var(--ink);
  text-decoration: none;
  overflow: hidden;
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease;
}

.latest-card::before {
  content: "";
  position: absolute;
  inset: -40%;
  background: radial-gradient(
    circle at 30% 26%,
    rgba(255, 255, 255, 0.5) 0 10%,
    transparent 46%
  );
  opacity: 0;
  transition: opacity 0.18s ease;
  pointer-events: none;
}

.latest-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow);
}

.latest-card:hover::before {
  opacity: 1;
}

.latest-card--red { background: var(--red); color: #fff; }
.latest-card--blue { background: var(--blue); color: #fff; }
.latest-card--green { background: var(--green); color: #fff; }
.latest-card--yellow { background: var(--yellow); }
.latest-card--purple { background: var(--purple); color: #fff; }

.latest-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.latest-number {
  font-size: 30px;
  font-weight: 900;
  line-height: 1;
  opacity: 0.85;
}

.latest-tags {
  max-width: 60%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 10px;
  font-weight: 900;
  opacity: 0.85;
}

.latest-photo {
  width: 100%;
  height: 120px;
  margin-bottom: 14px;
  object-fit: cover;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: inset 0 0 0 3px rgba(255, 255, 255, 0.2);
}

.latest-card h3 {
  margin: 0 0 8px;
  font-size: 21px;
  line-height: 1.15;
}

.latest-card p {
  margin: 0 0 14px;
  font-size: 13px;
  line-height: 1.55;
  opacity: 0.92;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.latest-meta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: auto;
  font-size: 11px;
  font-weight: 900;
  opacity: 0.85;
}

.journey-head {
  max-width: 620px;
  margin-bottom: 30px;
}

.journey-list {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.journey-item {
  position: relative;
  min-height: 210px;
  padding: 18px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow-sm);
}

.journey-item--ai {
  background: var(--purple);
  color: #fff;
}

.journey-step {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 14px;
  padding: 5px 9px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  font-size: 11px;
  font-weight: 900;
}

.journey-step--red { background: var(--red); color: #fff; }
.journey-step--blue { background: var(--blue); color: #fff; }
.journey-step--yellow { background: var(--yellow); }
.journey-step--green { background: var(--green); color: #fff; }
.journey-step--purple { background: var(--red); color: #fff; }

.journey-item h3 {
  margin: 0 0 8px;
  font-size: 19px;
  line-height: 1.15;
}

.journey-item p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.6;
  font-weight: 600;
}

.journey-item--ai p {
  color: rgba(255, 255, 255, 0.86);
}

.coming-soon {
  display: inline-block;
  margin-top: 16px;
  padding: 5px 9px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: var(--yellow);
  color: var(--ink);
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.05em;
}

.cta-section {
  margin: 0 20px 72px;
  border: 3px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  background: var(--yellow);
}

.cta-inner {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-top: 52px;
  padding-bottom: 52px;
}

.cta-inner .section-kicker {
  color: var(--red);
}

.cta-inner h2 {
  max-width: 18ch;
}

.cta-inner > p:not(.section-kicker) {
  max-width: 52ch;
  margin-bottom: 22px;
}

.cta-inner .brick-btn {
  gap: 8px;
}

.state-text {
  margin-top: 24px;
  color: var(--muted);
  font-weight: 700;
}

.state-text--error {
  color: var(--red);
}

@keyframes live-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 166, 81, 0.6); }
  50% { box-shadow: 0 0 0 8px rgba(0, 166, 81, 0); }
}

@media (max-width: 960px) {
  .latest-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .journey-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 700px) {
  .hero {
    min-height: 78svh;
  }

  .hero-inner {
    padding-top: 48px;
    padding-bottom: 48px;
  }

  .stats-strip,
  .latest-grid,
  .journey-list {
    grid-template-columns: 1fr;
  }

  .cta-section {
    margin-left: 10px;
    margin-right: 10px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .live-dot {
    animation: none;
  }
}
</style>
```

- [ ] **Step 3: Run build and verify it passes**

Run:

```bash
pnpm build
```

Expected: build succeeds.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Home.vue frontend/src/styles/bricks.css
git commit -m "feat: redesign homepage as lightweight portal"
```

---

### Task 8: Final Verification

**Files:**
- No source changes expected.

- [ ] **Step 1: Run the full unit test suite**

Run:

```bash
pnpm test
```

Expected: 7 tests PASS.

- [ ] **Step 2: Run the production build**

Run:

```bash
pnpm build
```

Expected: TypeScript and Vite build succeed.

- [ ] **Step 3: Start the dev server**

Run:

```bash
pnpm dev
```

Expected: Vite starts and prints a local URL.

- [ ] **Step 4: Browser smoke test**

Open these routes in the browser and verify no console errors:

```text
/
/browse
/post/1
```

Verify:

- Header contains a “书房” link.
- Homepage hero links to `/browse`.
- Homepage latest cards link to `/post/:id`.
- `/browse` filters by category, search, and `?tag=`.
- `/post/:id` renders Markdown and has a working back link.
- Desktop and mobile widths have no horizontal overflow and no overlapping text.

- [ ] **Step 5: Commit any remaining changes**

If the smoke test uncovered fixes, commit them with a clear message. Otherwise no commit is needed.

---

## Self-Review Notes

- Spec coverage: every page from the approved design has a task (`/`, `/browse`, `/post/:id`, navigation, assets, components, tests).
- Placeholder scan: no TBD/TODO entries; code blocks contain full implementations.
- Type consistency: all pages use the same `Post` interface from `src/api/posts.ts`, and utility names match across tests and components.
