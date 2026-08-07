# 项目结构如下：


```
it-grows/
│
├── backend/
│
├── frontend/
│
├── docs/
│
├── README.md
│
└── .gitignore
```

---

# 然后进入 backend

这里。

才是真正的 AI Agent Backend

第一版框架设计：

```
backend/

├── app/
│   │
│   ├── main.py          # FastAPI入口
│   │
│   ├── api/             # Router
│   │
│   ├── core/            # Config / Settings
│   │
│   ├── models/          # SQLModel
│   │
│   ├── schemas/         # Pydantic
│   │
│   ├── services/        # 业务逻辑
│   │
│   ├── repositories/    # 数据访问
│   │
│   └── utils/           # 工具函数
│
├── tests/
│
├── pyproject.toml  #类似package.json，记录运行项目需要什么-项目身份证
│
└── .env
```

Readme第一版只有下面这些内容：

```
# it grows 🌱

Grow a little.
Every single day.

## Vision

Build a second brain for AI founders.

## MVP

- Knowledge
- Blog
- AI Assistant

## Tech Stack

- FastAPI
- PostgreSQL
- SQLModel
- Redis
- OpenAI
```
