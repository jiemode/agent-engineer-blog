# Agent Engineer Blog

一个带 Agent 色彩的个人博客：Markdown 写作、JWT 登录、异步任务、RAG 知识库问答、流式 AI 助理。

## 架构

```
frontend/                  Vue 3 + Vite + TypeScript
backend/                   FastAPI + SQLModel（工业级分层）
  app/
    core/                  配置、数据库、安全、LLM、RAG、任务引擎
    models/                数据库表模型
    schemas/               请求/响应数据契约
    services/              业务逻辑层
    routers/               HTTP 入口层
    tasks/                 异步任务处理器
knowledge/                 RAG 知识库（Markdown 笔记）
```

分层原因：Router 只负责 HTTP，Service 只负责业务，Core 只负责基础设施，Models 管存储，Schemas 管契约。每一层职责单一，方便测试、替换和扩展。

## 本地运行

### 后端（uv）

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

### 前端

```powershell
cd frontend
pnpm install
pnpm run dev
```

## 导入 digital_garden 文章

博客内容来自 `digital_garden`。导入脚本只读源目录，并把文章写入数据库和 `knowledge/`：

```powershell
cd backend
uv run python -m scripts.import_digital_garden
```

默认读取 `E:\AI\Projects\digital_garden`；如果换了笔记目录：

```powershell
$env:DIGITAL_GARDEN_DIR = "E:\path\to\notes"
uv run python -m scripts.import_digital_garden
```

脚本可重复运行，标题相同的文章会更新，不会重复创建。

## 部署

前端可部署到 GitHub Pages（免费），后端部署到 Render（免费额度），数据库用 Neon（免费 PostgreSQL）。

详细步骤见 [docs/DEPLOY.md](./docs/DEPLOY.md)。
