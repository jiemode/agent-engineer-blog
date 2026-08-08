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
        v-for="stat in [
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
