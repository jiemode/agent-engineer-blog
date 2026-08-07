<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { clearToken, getToken } from './api/auth'

const router = useRouter()
const isLoggedIn = ref(Boolean(getToken()))

router.afterEach(() => {
  isLoggedIn.value = Boolean(getToken())
})

function logout() {
  clearToken()
  isLoggedIn.value = false
  router.push('/')
}
</script>

<template>
  <div class="site">
    <header class="site-header">
      <div class="header-inner page-shell">
        <router-link to="/" class="brand">
          <span class="logo-brick" aria-hidden="true">
            <span class="stud"></span>
            <span class="stud"></span>
            <span class="stud"></span>
            <span class="stud"></span>
          </span>
          <span class="brand-name">Agent Blog</span>
        </router-link>

        <nav class="header-nav" aria-label="主导航">
          <router-link to="/#posts" class="nav-link">浏览文章</router-link>
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
      </div>
      <div class="stud-strip" aria-hidden="true"></div>
    </header>

    <router-view />

    <!-- 全局页脚：把项目背后的技术栈和开源链接收拢在一起，访客不用登录也能了解来龙去脉 -->
    <footer class="site-footer">
      <div class="footer-inner page-shell">
        <div class="footer-brand">
          <span class="logo-brick logo-brick--small" aria-hidden="true">
            <span class="stud"></span>
            <span class="stud"></span>
            <span class="stud"></span>
            <span class="stud"></span>
          </span>
          <span>Agent Engineer Blog</span>
        </div>
        <p class="footer-note">
          Vue 3 + FastAPI + RAG + GitHub Pages + Render：一座从 0 到 1
          拼出来的 AI Agent 学习博客。
        </p>
        <div class="footer-links">
          <a
            href="https://github.com/jiemode/agent-engineer-blog"
            target="_blank"
            rel="noreferrer"
          >
            GitHub
          </a>
          <router-link to="/assistant">问笔记</router-link>
          <router-link to="/#posts">全部文章</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.site {
  min-height: 100svh;
  display: flex;
  flex-direction: column;
}

.site > :not(.site-header):not(.site-footer) {
  flex: 1 0 auto;
}

.site-header {
  background: var(--paper);
  border-bottom: 2px solid var(--ink);
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 14px;
  padding-bottom: 14px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--ink);
  font-weight: 900;
  font-size: 18px;
  text-decoration: none;
}

.logo-brick {
  display: grid;
  grid-template-columns: repeat(2, 12px);
  gap: 3px;
  padding: 5px;
  background: var(--red);
  border: 2px solid var(--ink);
  border-radius: 2px;
}

.logo-brick--small {
  grid-template-columns: repeat(2, 9px);
  padding: 4px;
  background: var(--blue);
}

.stud {
  width: 12px;
  height: 12px;
  border: 2px solid var(--ink);
  border-radius: 50%;
  background: var(--yellow);
  box-shadow:
    inset 2px 2px 0 rgba(255, 255, 255, 0.85),
    inset -2px -2px 0 rgba(0, 0, 0, 0.18);
}

.logo-brick--small .stud {
  width: 9px;
  height: 9px;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.nav-link {
  padding: 6px 2px;
  color: var(--ink);
  font-size: 15px;
  font-weight: 800;
  text-decoration: none;
}

.nav-link:hover {
  text-decoration: underline;
  text-underline-offset: 4px;
}

.nav-link--button {
  background: none;
  border: none;
  cursor: pointer;
}

.stud-strip {
  margin-top: -2px;
}

/* 页脚：黑色底 + 白色文字，与乐高积木的“底座”呼应 */
.site-footer {
  flex-shrink: 0;
  margin-top: auto;
  border-top: 3px solid var(--ink);
  background: var(--ink);
  color: #fff;
}

.footer-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 18px;
  padding-top: 22px;
  padding-bottom: 22px;
}

.footer-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 900;
}

.footer-note {
  max-width: 46ch;
  margin: 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
  line-height: 1.6;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.footer-links a {
  color: var(--yellow);
  font-size: 13px;
  font-weight: 800;
  text-decoration: none;
}

.footer-links a:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

@media (max-width: 720px) {
  .footer-inner {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
