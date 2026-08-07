---
title: vite.config 逐行拆解与 TypeScript 速成
description: 从一行 proxy 配置开始，迈出前端 TypeScript 的第一步
---

# vite.config 逐行拆解与 TypeScript 速成

第一次看到 `vite.config.ts` 时，我的内心是：“TypeScript 是什么？我连看都看不懂。”后来发现，TypeScript 不是一门新语言，它是 JavaScript 加上“给数据立规矩”的类型系统。而且我们这份配置文件里几乎没写类型，因为它简单到 TS 能自己猜出来。

## 1. 逐行拆解这份配置

```ts
import { defineConfig } from 'vite'      // 从 vite 包里拿 defineConfig 这个函数
import vue from '@vitejs/plugin-vue'     // 从 vue 插件包里拿 vue 插件

export default defineConfig({            // 把这个配置对象导出给 Vite 用
  plugins: [vue()],                      // 告诉 Vite：请启用 Vue 插件
  server: {
    proxy: {                             // 开发服务器做转发
      '/api': {
        target: 'http://127.0.0.1:8000', // 凡是 /api 开头的请求，转发到后端
        changeOrigin: true,              // 让后端觉得请求来自它自己
      },
    },
  },
})
```

只需要认识这几个东西：

- `import ... from '...'`：从别人写的包里借一个工具进来。
- `export default ...`：把自己写的东西交出去给别人用。
- 花括号 `{}` 是对象，中括号 `[]` 是数组，括号 `()` 是调用函数。
- `defineConfig({...})`：Vite 提供的带类型提示的配置函数，传一个对象进去，它会检查你有没有写错键名。

## 2. proxy 是干嘛的

前端开发服务器跑在 5173，后端跑在 8000。如果前端直接请求 `http://127.0.0.1:8000/api/posts`，浏览器会触发跨域问题。有了 proxy：

```text
浏览器请求  http://localhost:5173/api/posts
     ↓ Vite 偷偷转发
后端收到    http://127.0.0.1:8000/api/posts
```

浏览器以为自己一直在和 5173 说话，实际数据是后端给的。这就是为什么 axios 以后可以只写 `/api/posts`，不用写完整地址。

## 3. TypeScript 速成四块

### 3.1 变量类型

```ts
let name: string = "Codex"
let count: number = 3
let isAdmin: boolean = true
```

### 3.2 给对象画一张图（interface）

```ts
interface Post {
  id: number
  title: string
  content: string
}
```

这和我们后端用 Pydantic 定义 `BlogPost` 是同一个思想：先规定数据长什么样。

### 3.3 数组

```ts
const posts: Post[] = [
  { id: 1, title: "第一篇", content: "你好" },
]
```

### 3.4 泛型（先眼熟，不用背）

```ts
const posts = ref<Post[]>([])   // Vue 里：一个装着 Post 数组的响应式变量
```

`<Post[]>` 就是泛型，意思是“这个 ref 里面装的是一堆 Post”。在 Vue 项目里会天天见到，但不用急着背定义，看多了自然懂。

## 4. 为什么不用先刷完整本 TS 教程

真正的成长路线是：先跑项目，遇到不懂的语法再回头补。做 Vue 前端时最常见的 TS 场景就是：

```text
定义 Post 接口
用 ref<Post[]>([]) 装文章列表
用 axios.get<Post[]>('/api/posts') 拿数据
```

把这四块看懂，已经够撑过整个前端阶段。

## 面试一句话总结

TypeScript 是带类型的 JavaScript；interface 定义数据结构，泛型规定容器里装什么；vite.config 里的 proxy 让前端开发服务器把 `/api` 请求转发到后端，绕过浏览器跨域限制。
