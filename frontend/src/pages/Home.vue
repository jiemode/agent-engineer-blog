<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import { deletePost, fetchPosts, type Post } from '../api/posts'
import { getToken } from '../api/auth'
import legoPile from '../assets/lego-pile.jpg'
import legoFrozen from '../assets/lego-frozen.jpg'
import legoDuplo from '../assets/lego-duplo.jpg'

// 文章数据与页面状态
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

// 把每篇文章的 tags 字段拆成分类，并统计每个分类的文章数量
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

// 支持“分类 + 关键词”同时筛选，关键词会同时匹配标题和正文
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

// 最近发布的文章：按 id 倒序，最多展示 6 篇，放在“最近更新”横向卡片区
const latestPosts = computed(() =>
  [...posts.value].sort((a, b) => b.id - a.id).slice(0, 6),
)

// 把 Markdown 正文里的小标题、列表项、代码块数量当作“知识块”，让访问者一眼看到内容密度
const knowledgeBlocks = computed(() =>
  posts.value.reduce((total, post) => {
    const headings = post.content.match(/^#{1,6}\s/gm)?.length ?? 0
    const bullets = post.content.match(/^[-*+]\s/gm)?.length ?? 0
    const fences = post.content.match(/```/g)?.length ?? 0
    return total + headings + bullets + fences
  }, 0),
)

const totalChars = computed(() =>
  posts.value.reduce((total, post) => total + post.content.length, 0),
)

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

// 能力区静态数据：每张卡都对应一个 Agent 博客真实用到的技术点
interface Capability {
  index: string
  title: string
  text: string
  tone: 'red' | 'blue' | 'green' | 'yellow' | 'purple'
  tag: string
  wide?: boolean
  tall?: boolean
  image?: string
}

const capabilities: Capability[] = [
  {
    index: '01',
    title: 'RAG 笔记问答',
    text: 'AI 先从你自己的 Markdown 知识库里检索依据，再结合上下文作答。回答不靠猜，而是带着出处回来。',
    tone: 'red',
    tag: 'RETRIEVAL',
    wide: true,
    image: legoFrozen,
  },
  {
    index: '02',
    title: '流式对话',
    text: '打字机式输出与多轮上下文记忆，让助理像真人一样边想边写。',
    tone: 'blue',
    tag: 'STREAMING',
    tall: true,
  },
  {
    index: '03',
    title: '分层架构',
    text: 'Router → Service → Model，各层各司其职。每一块乐高都能单独替换、测试和解释。',
    tone: 'yellow',
    tag: 'ARCHITECTURE',
    wide: true,
  },
  {
    index: '04',
    title: '安全发布',
    text: 'JWT 登录保护写作入口，Markdown 实时预览，发布后首页立刻更新。',
    tone: 'green',
    tag: 'PUBLISHING',
  },
  {
    index: '05',
    title: '自动化部署',
    text: 'GitHub Actions 负责构建前端，Render 托管 API，Postgres 存数据。一次推送，全球访问。',
    tone: 'purple',
    tag: 'DEPLOY',
  },
]

// 成长路线静态数据：从“看懂请求”到“跑通上线”的 0 → 1 过程
const journey = [
  {
    step: 'STEP 01',
    title: '看懂一次请求',
    text: '从 FastAPI 的 Schema、Router、Service 开始，理解“谁负责接客、谁负责干活”。',
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

// 首页统计条：不用登录也能看到这座“知识乐园”的规模
const stats = computed(() => [
  { label: '文章', value: posts.value.length, suffix: '篇', tone: 'red' },
  { label: '分类', value: categories.value.length, suffix: '个', tone: 'blue' },
  { label: '知识块', value: knowledgeBlocks.value, suffix: '块', tone: 'yellow' },
  { label: '总字数', value: totalChars.value, suffix: '字', tone: 'green' },
])
</script>

<template>
  <main class="home">
    <!-- 全屏积木图 Hero：访客第一眼看到的不再是空按钮，而是一座“正在搭建”的知识世界 -->
    <section class="hero">
      <img
        class="hero-photo"
        :src="legoPile"
        alt="五颜六色的积木堆，代表可以被自由拼装的 AI 知识与技术栈"
      />
      <div class="hero-veil" aria-hidden="true"></div>
      <div class="hero-sparks" aria-hidden="true">
        <span></span><span></span><span></span><span></span><span></span>
      </div>

      <div class="hero-inner page-shell">
        <p class="eyebrow">
          <span class="live-dot"></span>
          A BLOG BUILT LIKE A BRICK SET
        </p>
        <h1>一座可拼装的<br />知识世界</h1>
        <p class="hero-lead">
          从零开始做 AI Agent 的完整旅程：写接口、建知识库、训练助理、部署上线。
          每篇文章都是一块积木，随时可以拆开、重组、复用。
        </p>
        <div class="hero-actions">
          <router-link to="/assistant" class="brick-btn brick-btn--yellow">
            问我的笔记
          </router-link>
          <router-link v-if="isLoggedIn" to="/new" class="brick-btn brick-btn--red">
            写新文章
          </router-link>
          <router-link v-else to="/login" class="brick-btn brick-btn--red">
            登录后写作
          </router-link>
          <a href="#posts" class="brick-btn brick-btn--ghost">浏览文章</a>
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

    <!-- 简介区：未登录访客也能读懂“这个博客到底在做什么” -->
    <section class="intro-section page-shell">
      <div class="intro-copy">
        <p class="section-kicker">WHAT IS THIS</p>
        <h2>为什么叫 Agent 博客？</h2>
        <p>
          普通的博客是“看完就走”；这里的博客是一套可以互相咬合的知识积木。
          你写下的每一个问题、每一段踩坑记录，都会进入知识库，成为 AI 助理回答下一个问题时的依据。
        </p>
        <div class="intro-points">
          <span>写作即建库</span>
          <span>提问即检索</span>
          <span>上线即成长</span>
        </div>
      </div>

      <div class="intro-visual">
        <img :src="legoDuplo" alt="积木特写，代表博客内容的模块化" />
        <div class="intro-tag intro-tag--yellow">NOTES → KNOWLEDGE</div>
        <div class="intro-tag intro-tag--red">QUESTION → ANSWER</div>
      </div>
    </section>

    <!-- 数据统计：文章、分类、知识块、总字数，全部由真实数据计算 -->
    <section class="stats-strip page-shell" aria-label="博客数据统计">
      <div
        v-for="stat in stats"
        :key="stat.label"
        :class="['stat-brick', `stat-brick--${stat.tone}`]"
      >
        <span class="stat-value">{{ stat.value.toLocaleString() }}</span>
        <span class="stat-label">{{ stat.label }} {{ stat.suffix }}</span>
      </div>
    </section>

    <!-- Bento Grid：Aceternity 风格的能力展示，每张卡都是一块“可拼装”的技术积木 -->
    <section class="bento-section page-shell">
      <div class="section-head">
        <p class="section-kicker">BUILDING BLOCKS</p>
        <h2>这套博客能拼出什么</h2>
        <p>没有魔法，只有一个个可以独立理解、组合、替换的技术积木。</p>
      </div>

      <div class="bento-grid">
        <article
          v-for="capability in capabilities"
          :key="capability.index"
          :class="[
            'bento-card',
            `bento-card--${capability.tone}`,
            { 'bento-card--wide': capability.wide, 'bento-card--tall': capability.tall },
          ]"
        >
          <div class="stud-strip" aria-hidden="true"></div>
          <div class="bento-top">
            <span class="bento-index">{{ capability.index }}</span>
            <span class="bento-tag">{{ capability.tag }}</span>
          </div>
          <h3>{{ capability.title }}</h3>
          <p>{{ capability.text }}</p>
          <img
            v-if="capability.image"
            class="bento-photo"
            :src="capability.image"
            alt="彩色积木特写"
          />
        </article>
      </div>
    </section>

    <!-- 成长路线：0 → 1 的时间线，也是面试时可以讲出来的“项目叙事” -->
    <section class="journey-section page-shell">
      <div class="section-head section-head--left">
        <p class="section-kicker">LEARNING PATH</p>
        <h2>从 0 到 1 的成长路线</h2>
        <p>每一关都在真实项目里发生过：踩坑、复盘、写进博客、变成能力。</p>
      </div>

      <ol class="journey-list">
        <li v-for="item in journey" :key="item.step" class="journey-item">
          <span :class="['journey-step', `journey-step--${item.color}`]">
            {{ item.step }}
          </span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </li>
      </ol>
    </section>

    <!-- 最近更新：横向卡片流，先给访客最鲜活的几块积木 -->
    <section class="latest-section page-shell" aria-label="最近更新">
      <div class="section-head section-head--left">
        <p class="section-kicker">LATEST BRICKS</p>
        <h2>最近更新</h2>
        <p>最新拼上的几块知识积木，先睹为快。</p>
      </div>

      <div v-if="loading" class="state-text">加载中...</div>
      <p v-else-if="error" class="state-text state-text--error">{{ error }}</p>
      <div v-else-if="latestPosts.length" class="latest-row">
        <article
          v-for="(post, index) in latestPosts"
          :key="post.id"
          :class="['latest-card', `latest-card--${categoryColor(index)}`]"
        >
          <div class="latest-card-top">
            <span class="latest-number">{{ String(post.id).padStart(2, '0') }}</span>
            <span class="latest-tags">{{ post.tags || 'UNTAGGED' }}</span>
          </div>
          <h3>{{ post.title }}</h3>
          <p>{{ post.content.replace(/[#*`>_]/g, '').slice(0, 96) }}...</p>
          <div class="latest-meta">{{ post.created_at }}</div>
        </article>
      </div>
      <p v-else class="state-text">还没有文章，等第一块积木出现。</p>
    </section>

    <!-- 文章总览：保留分类筛选、搜索和完整列表 -->
    <section id="posts" class="browse-section page-shell">
      <div class="browse-head">
        <div>
          <p class="section-kicker">ALL BRICKS</p>
          <h2>按知识领域漫游</h2>
        </div>
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
            {{ category.name }} 路 {{ category.count }}
          </button>
        </div>
      </div>

      <div class="search-row">
        <input v-model="search" placeholder="搜索文章标题或正文" />
      </div>

      <p v-if="loading" class="state-text">加载中...</p>
      <p v-if="error" class="state-text state-text--error">{{ error }}</p>
      <p v-if="!loading && !error && filteredPosts.length === 0" class="state-text">
        还没有文章，拼第一块砖吧。
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
            <div class="post-meta">#{{ post.id }} 路 {{ post.created_at }}</div>
            <MarkdownRenderer :content="post.content" />
          </div>
        </article>
      </section>
    </section>

    <!-- 收尾 CTA：即使不登录，也邀请访客来“问一问”这座知识库 -->
    <section class="cta-section">
      <div class="cta-inner page-shell">
        <p class="section-kicker">TRY THE ASSISTANT</p>
        <h2>把笔记交给 Agent</h2>
        <p>用自然语言提问，AI 会从这些博客里找出答案和出处。</p>
        <router-link to="/assistant" class="brick-btn brick-btn--yellow">
          开始提问
        </router-link>
      </div>
    </section>
  </main>
</template>

<style scoped>
/* 页面顶部结构：Hero 使用全屏真实积木图，文字直接叠在图上，形成“身临其境”的第一屏 */
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

/* 闪光粒子：用纯 CSS 模拟 Aceternity Sparkles，像积木上反射的高光 */
.hero-sparks {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.hero-sparks span {
  position: absolute;
  width: 8px;
  height: 8px;
  border: 2px solid var(--ink);
  background: var(--yellow);
  transform: rotate(45deg);
  animation: sparkle-float 5s ease-in-out infinite;
}

.hero-sparks span:nth-child(1) { top: 18%; left: 12%; animation-delay: 0s; }
.hero-sparks span:nth-child(2) { top: 30%; left: 78%; animation-delay: 0.8s; background: var(--green); }
.hero-sparks span:nth-child(3) { top: 58%; left: 88%; animation-delay: 1.6s; background: var(--red); }
.hero-sparks span:nth-child(4) { top: 74%; left: 8%; animation-delay: 2.2s; background: var(--blue); }
.hero-sparks span:nth-child(5) { top: 44%; left: 60%; animation-delay: 3s; background: var(--purple); }

/* 简介区：左侧讲“为什么”，右侧放积木特写，形成图文对照 */
.intro-section {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.9fr);
  gap: 48px;
  align-items: center;
  padding-top: 72px;
  padding-bottom: 72px;
}

.section-kicker {
  color: var(--blue);
  text-transform: uppercase;
}

.intro-copy h2,
.section-head h2,
.journey-section h2,
.browse-head h2,
.cta-inner h2 {
  margin: 0 0 14px;
  font-size: clamp(30px, 4vw, 46px);
  line-height: 1.04;
}

.intro-copy > p:not(.section-kicker),
.section-head > p:not(.section-kicker),
.journey-section .section-head--left > p:not(.section-kicker),
.latest-section .section-head--left > p:not(.section-kicker),
.cta-inner > p:not(.section-kicker) {
  margin: 0;
  color: var(--muted);
  font-size: 16px;
  line-height: 1.7;
  font-weight: 600;
}

.intro-points {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 22px;
}

.intro-points span {
  padding: 8px 12px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow-sm);
  font-size: 13px;
  font-weight: 900;
}

.intro-visual {
  position: relative;
  min-height: 280px;
}

.intro-visual img {
  width: 100%;
  height: 320px;
  object-fit: cover;
  border: 3px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.intro-tag {
  position: absolute;
  padding: 7px 11px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  font-size: 12px;
  font-weight: 900;
}

.intro-tag--yellow {
  top: -14px;
  right: 18px;
  background: var(--yellow);
  transform: rotate(3deg);
}

.intro-tag--red {
  bottom: 26px;
  left: -14px;
  background: var(--red);
  color: #fff;
  transform: rotate(-4deg);
}

/* 数据统计条：四个等宽的“数字积木”，不用登录也能看到博客规模 */
.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  padding-bottom: 24px;
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

/* Bento Grid：借鉴 Aceternity 的非对称网格布局，用乐高描边和硬阴影保持设计语言统一 */
.bento-section {
  padding-top: 64px;
  padding-bottom: 72px;
}

.section-head {
  max-width: 620px;
  margin-bottom: 34px;
}

.section-head--left {
  margin-left: 0;
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-auto-rows: 232px;
  gap: 18px;
}

.bento-card {
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 18px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease;
}

.bento-card:hover {
  transform: translate(-3px, -3px) rotate(-0.4deg);
  box-shadow: 8px 8px 0 var(--ink);
}

.bento-card--red { background: var(--red); color: #fff; }
.bento-card--blue { background: var(--blue); color: #fff; }
.bento-card--green { background: var(--green); color: #fff; }
.bento-card--purple { background: var(--purple); color: #fff; }
.bento-card--yellow { background: var(--yellow); color: var(--ink); }

.bento-card--wide {
  grid-column: span 2;
}

.bento-card--tall {
  grid-row: span 2;
}

.bento-card .stud-strip {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 12px;
  border-top: 0;
  background: rgba(255, 255, 255, 0.28);
}

.bento-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.bento-index {
  font-size: 32px;
  font-weight: 900;
  line-height: 1;
  opacity: 0.9;
}

.bento-tag {
  padding: 5px 8px;
  border: 2px solid currentColor;
  border-radius: var(--radius);
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.06em;
}

.bento-card h3 {
  margin: 0 0 10px;
  font-size: 24px;
  line-height: 1.08;
}

.bento-card p {
  max-width: 46ch;
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  font-weight: 600;
  opacity: 0.92;
}

.bento-photo {
  width: 100%;
  height: 132px;
  margin-top: auto;
  object-fit: cover;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: inset 0 0 0 3px rgba(255, 255, 255, 0.2);
}

/* 成长路线：编号 + 文字的时间线，横屏排列，移动端自然折行 */
.journey-section {
  padding-top: 64px;
  padding-bottom: 72px;
}

.journey-list {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.journey-item {
  position: relative;
  padding: 20px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow-sm);
}

.journey-item::before {
  content: "";
  position: absolute;
  top: 20px;
  right: -16px;
  width: 12px;
  height: 12px;
  border: 2px solid var(--ink);
  border-radius: 50%;
  background: var(--yellow);
  z-index: 1;
}

.journey-item:last-child::before {
  display: none;
}

.journey-step {
  display: inline-flex;
  margin-bottom: 14px;
  padding: 5px 9px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.05em;
}

.journey-step--red { background: var(--red); color: #fff; }
.journey-step--blue { background: var(--blue); color: #fff; }
.journey-step--yellow { background: var(--yellow); }
.journey-step--green { background: var(--green); color: #fff; }

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

/* 最近更新：横向卡片流，移动端可横向滑动，桌面端直接平铺 */
.latest-section {
  padding-top: 56px;
  padding-bottom: 56px;
}

.latest-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 8px;
}

.latest-card {
  min-height: 190px;
  padding: 18px;
  border: 2px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease;
}

.latest-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow);
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
  margin-bottom: 16px;
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
  letter-spacing: 0.05em;
}

.latest-card h3 {
  margin: 0 0 8px;
  font-size: 19px;
  line-height: 1.2;
}

.latest-card p {
  margin: 0 0 12px;
  font-size: 13px;
  line-height: 1.55;
  opacity: 0.9;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.latest-meta {
  margin-top: auto;
  font-size: 11px;
  font-weight: 800;
  opacity: 0.8;
}

/* 文章总览区：保留原有分类筛选、搜索和完整文章列表 */
.browse-section {
  padding-top: 56px;
  padding-bottom: 72px;
}

.browse-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 20px;
}

.browse-head h2 {
  margin-bottom: 0;
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

.category-brick--red .mini-stud { background: var(--red); }
.category-brick--blue .mini-stud { background: var(--blue); }
.category-brick--green .mini-stud { background: var(--green); }
.category-brick--yellow .mini-stud { background: var(--yellow); }
.category-brick--purple .mini-stud { background: var(--purple); }

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

/* 收尾 CTA：整条乐高黄色横幅，邀请访客与 AI 助理互动 */
.cta-section {
  margin: 0 20px 72px;
  border: 3px solid var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  background:
    radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 0.75) 0 6%, transparent 7%),
    radial-gradient(circle at 48% 70%, rgba(255, 255, 255, 0.7) 0 5%, transparent 6%),
    var(--yellow);
  background-size: 84px 84px;
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

@keyframes live-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 166, 81, 0.6); }
  50% { box-shadow: 0 0 0 8px rgba(0, 166, 81, 0); }
}

@keyframes sparkle-float {
  0%, 100% {
    transform: translateY(0) rotate(45deg) scale(1);
    opacity: 0.9;
  }
  50% {
    transform: translateY(-18px) rotate(45deg) scale(1.35);
    opacity: 0.45;
  }
}

@media (max-width: 960px) {
  .intro-section {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .bento-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .bento-card--wide {
    grid-column: span 2;
  }

  .journey-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .journey-item:nth-child(2)::before {
    display: none;
  }

  .latest-row {
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
  .bento-grid,
  .journey-list,
  .latest-row {
    grid-template-columns: 1fr;
  }

  .bento-card--wide,
  .bento-card--tall {
    grid-column: span 1;
    grid-row: span 1;
  }

  .bento-card--tall {
    min-height: 300px;
  }

  .journey-item::before,
  .journey-item:nth-child(2)::before {
    display: none;
  }

  .post-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .post-number {
    font-size: 30px;
  }

  .cta-section {
    margin-left: 10px;
    margin-right: 10px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .live-dot,
  .hero-sparks span {
    animation: none;
  }
}
</style>
