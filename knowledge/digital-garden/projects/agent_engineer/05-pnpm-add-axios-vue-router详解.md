---
title: pnpm add axios vue-router 详解
description: 前端两个基础包：axios 负责和后端聊天，vue-router 负责页面跳转
---

# pnpm add axios vue-router 详解

这是我准备做 Vue 前端时补的一课。第一次看到 `pnpm add axios vue-router` 时我只有一个疑问：这是在装什么，为什么要装？现在我知道了，这一行是在买两个“前端必备工具”。

## 1. 这行命令到底做了什么

```powershell
pnpm add axios vue-router
```

拆开看：

- `pnpm`：包管理器，相当于快递员，负责把别人的代码从 npm 仓库拿到我们项目里。
- `add`：安装并记录，装完还会写进 `package.json` 的 `dependencies`。
- `axios` 和 `vue-router`：两个不同的包。

装完之后：

- `package.json` 里多出两个依赖记录
- `node_modules` 里多出它们的实际代码
- 别人拿到项目执行 `pnpm install` 也能装齐

## 2. axios：让网页和后端聊天

我们的后端已经有这些接口：

```text
GET    /api/posts        文章列表
POST   /api/posts        新建文章
POST   /api/auth/login   登录
```

但 Vue 页面不会自己打电话，必须用一个 HTTP 客户端去请求后端。`axios` 就是干这个的：发请求、收响应、处理 JSON。

它比浏览器自带的 `fetch` 更方便的地方是支持拦截器：

- 在请求发出前，统一加上 `Authorization: Bearer <token>`
- 在响应回来时，遇到 401 自动去刷新 token

这正是 `code` 项目前端 `src/request/index.ts` 里做的事情。

## 3. vue-router：让网页有页面跳转

没有它，Vue 页面永远是同一个页面。有了它，我们才有：

```text
/          首页（博客列表）
/post/1    文章详情
/login     登录页
/admin     写文章
```

它还支持路由守卫，比如“没登录的人不能进 /admin”，会先跳到 /login。对应 `code` 项目里 `frontend/src/routes/index.ts` 的 `beforeEach`。

## 4. 一个容易记住的类比

- `package.json` = 购物清单
- `node_modules` = 本地仓库
- `pnpm add axios vue-router` = 下单买两个工具放进仓库，同时把清单记好

## 5. 正式依赖 vs 开发依赖

```powershell
pnpm add axios vue-router   # 正式依赖，上线也要用
pnpm add -D typescript      # -D 是开发依赖，只有开发时用
```

## 面试一句话总结

`axios` 是前端的 HTTP 客户端，负责请求后端接口并统一处理 token；`vue-router` 是 Vue 的路由库，负责页面切换和登录守卫；`pnpm add` 则是把它们安装并记录进 `package.json`。
