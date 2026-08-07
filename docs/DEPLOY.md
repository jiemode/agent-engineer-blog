# 免费上线指南：GitHub Pages + Render + Neon

## 总体架构

```text
GitHub Pages  →  Vue 前端（静态、免费、好看）
Render        →  FastAPI 后端 + AI 助理（免费 Web Service）
Neon          →  PostgreSQL 数据库（免费、云端、不丢数据）
```

## 第 1 步：把项目推到 GitHub

1. 在 GitHub 网页上新建一个仓库，例如 `agent-engineer-blog`，不要勾选自动生成 README。
2. 在项目根目录打开 PowerShell，执行：

```powershell
cd E:\AI\Projects\agent_engineer
git init
git add .
git commit -m "feat: agent engineer blog"
git branch -M main
git remote add origin https://github.com/你的用户名/agent-engineer-blog.git
git push -u origin main
```

注意：`.env`、`blog.db`、`.venv`、`node_modules` 已被 `.gitignore` 排除，不会上传。

## 第 2 步：部署前端到 GitHub Pages

仓库里已经有 `.github/workflows/deploy-frontend.yml`，它会在每次 push 到 main 时自动构建并部署前端。

1. 打开仓库 Settings -> Pages。
2. Source 选择 `GitHub Actions`。
3. 等待工作流跑完，访问 `https://你的用户名.github.io/agent-engineer-blog/`。

## 第 3 步：创建 Neon 数据库（免费 PostgreSQL）

1. 打开 https://neon.tech ，注册并创建项目。
2. 复制连接字符串，格式类似：

```text
postgresql+psycopg://用户名:密码@ep-xxx.aws.neon.tech/数据库名?sslmode=require
```

3. 如果连接串开头是 `postgres://`，记得改成 `postgresql+psycopg://`。

## 第 4 步：部署后端到 Render（免费）

1. 打开 https://render.com ，用 GitHub 账号登录。
2. New -> Blueprint -> 选择 `agent-engineer-blog` 仓库，Render 会读取 `render.yaml`。
3. 部署前需要在 Render 控制台给服务填环境变量：

```text
DATABASE_URL   = Neon 的连接串
SECRET_KEY     = 一长串随机字符
LLM_API_KEY    = 你的 DeepSeek key
```

4. 部署完成后，后端地址类似 `https://agent-engineer-blog-api.onrender.com`。
5. 打开 `https://agent-engineer-blog-api.onrender.com/api/health`，应返回 `{"status":"ok"}`。

## 第 5 步：让前端指向后端

1. 打开 GitHub 仓库 Settings -> Secrets and variables -> Actions -> Variables。
2. 新增变量：

```text
VITE_API_BASE_URL = https://agent-engineer-blog-api.onrender.com
```

3. 重新 push 一次代码（或手动重跑工作流），前端就会用这个地址请求后端。

## 本地切换到 PostgreSQL（可选）

```powershell
cd E:\AI\Projects\agent_engineer
docker compose up -d
```

然后把 `backend/.env` 里的数据库连接改成：

```text
DATABASE_URL=postgresql+psycopg://agent:agent@127.0.0.1:5432/agent_blog
```

重启后端，`create_db_and_tables()` 会自动在 PostgreSQL 里建表。

## 常见问题

- 前端部署了但文章加载失败：检查 `VITE_API_BASE_URL` 是否已设置、后端是否在运行。
- Render 冷启动慢：免费实例空闲 15 分钟后休眠，这是正常的，几秒后会自动唤醒。
- 数据丢失：生产环境不要用 SQLite，一定要用 Neon 的 `DATABASE_URL`。
