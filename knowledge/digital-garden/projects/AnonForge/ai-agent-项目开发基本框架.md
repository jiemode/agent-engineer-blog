# ai-agent-项目开发基本框架
大项目最重要的就是各司其职，所以在开发之初就要确定好项目架构，这样才好有的放矢

我个人的基础脚手架如下：
```
my-agent-template/
│
├── frontend/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── agents/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── workflows/      # AI 工作流（LangGraph、PydanticAI 等）
│   │
│   ├── tests/              # 自动化测试
│   ├── requirements.txt
│   └── run.py
│
├── data/
├── docs/                   # 产品和技术文档
├── docker/
├── scripts/                # 初始化、部署、迁移等脚本
├── .env.example            # 环境变量模板
├── .gitignore
├── README.md
└── AGENTS.md
```

根据这个脚手架，anonforge这个项目的详细架构初步设计为：
```
├─ frontend/                           # 前端项目根目录
├─ backend/                            # 后端项目根目录
│   ├── app/                             # 应用主模块（核心业务代码所在）
│   │   ├── __init__.py               # 将 app 标记为 Python 包
│   │   ├── main.py                  # FastAPI 应用入口，创建 app 实例、注册路由、中间件等
│   │   ├── core/                      # 核心类库（配置管理类，数据库管理类）
│   │   │   ├── config.py          # 配置管理（读取环境变量、全局配置项）
│   │   │   ├── database.py      # 数据库连接与会话管理（如 SQLAlchemy engine/session）
│   │   ├── models/                  # ORM 模型定义（数据库表结构映射）
│   │   ├── schemas/                # 数据校验与序列化（Pydantic 模型，用于请求/响应）
│   │   ├── routers/                  # 路由层（API 接口定义，按业务拆分）
│   │   │   ├── api.py                # 总路由（设置/api前缀，并统一接入routes下的所有的路由对象）
│   │   │   ├── project.py          # 项目相关接口
│   │   │   ├── novel.py             # 小说/内容相关接口
│   │   │   ├── script.py             # 剧本相关接口
│   │   │   ├── production.py    # 生产/生成流程相关接口
│   │   │   ├── workbench.py    # 工作台/控制台接口
│   │   │   ├── task.py                # 任务管理接口（异步任务/队列等）
│   │   │   └── setting.py            # 系统设置相关接口
│   │   ├── agents/                     # 智能体/AI代理逻辑（如多Agent协作）
│   │   │   └── crew.py                # Agent编排或协同逻辑（任务分配、流程控制）
│   │   ├── services/                    # 服务层（业务逻辑封装，解耦路由与数据层）
│   │   │   └── vendor.py             # 第三方服务或供应商相关业务逻辑
│   │   └── utils/                          # 工具模块（通用功能，不直接包含业务逻辑）
│   │       ├── oss.py                    # 对象存储服务封装（如阿里云 OSS / S3）
│   │       └── xml_parser.py        # XML解析工具
│   ├── run.py                             # 项目启动文件（开发环境下）
│   └── requirements.txt             # Python 依赖列表
├─ data/                                      # 本地数据存储（缓存文件、测试数据、导出文件等）
├─ docker/                                  # docker配置存储（Dockerfile、docker-compose.yaml）
├─ .env                                       # 环境变量配置（数据库连接、密钥等敏感信息），本地叫.env，线上叫.env.production
└─ AGENTS.md / CLAUDE.md    # 项目根目录下的 AI 开发规范
```



