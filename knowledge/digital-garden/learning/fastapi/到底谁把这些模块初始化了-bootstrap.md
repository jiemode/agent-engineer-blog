# 我们现在有了一堆模块

我们现在已经有了：

```
Router
```

负责 HTTP。

还有：

```
Service
```

负责业务。

还有：

```
Repository
```

负责数据库。

还有：

```
Agent
```

负责 AI。

那么问题来了。

**谁来创建它们？**

例如：

```
chat_service = ChatService(...)
```

这一句应该写在哪里？

**不用写，有人会替你准备好的**
# 是谁准备好的？

答案就是：

> **应用启动的时候（Application Startup）。**

这里就是很多人第一次接触大型项目时觉得最神奇的地方。

程序启动时，不只是：

```
app = FastAPI()
```

真正的大项目启动时，会做很多准备工作。

例如：

```
启动程序

↓

读取 .env

↓

创建 Settings

↓

连接数据库

↓

创建 Redis Client

↓

创建 OpenAI Client

↓

创建 ChatRepository

↓

创建 ChatService

↓

注册 Router

↓

开始监听 8000 端口
```

注意！

很多对象不是在**请求来了以后**才创建的。

而是在**程序启动时**就已经准备好了。

# 为什么这样做？

想象一下如果每来一个用户都：

```
OpenAI()

Database()

Redis()
```

是不是很浪费？

尤其是数据库连接，数据库连接不是随便创建的，它很昂贵。

真正的大项目都会维护：

```
连接池（Connection Pool）
```

程序启动时建立，请求来了复用，请求结束归还

而不是不停地创建

# 于是，我们得到一个新的角色

今天，我们正式引入它。

```
Application（应用）

        │

        ▼

创建所有共享资源

        │

        ▼

把资源交给 Router
```

这就是整个系统真正的"组装者"。

---

# 那 Depends 到底做了什么？

在看到：
```
@router.post("/chat")
async def chat(
    service = Depends(get_chat_service)
):
    ...
```

你的脑子应该自动翻译成：

> **"我需要一个 ChatService，请帮我准备好。"**

不是：

```
service = ChatService(...)
```

而是：

```
我声明需要。

FastAPI 提供。
```

---

# 我们的 AI Agent 项目以后会怎么组装？


```
                   Application

                         │

        ┌────────────────────────────────┐

        ▼                                ▼

    Settings                        Database

        │                                │

        ▼                                ▼

     Redis                         OpenAIClient

        │                                │

        └──────────────┬─────────────────┘

                       ▼

                  ChatRepository

                       │

                       ▼

                   ChatService

                       │

                       ▼

                    Router

                       │

                       ▼

                   HTTP Request
```

注意观察。

数据流和依赖方向是不一样的。

---

## 数据流（请求来了以后）

```
HTTP

↓

Router

↓

Service

↓

Repository

↓

Database
```

这是：

**业务执行流程。**

---

## 依赖关系（程序启动时）

```
Database

↓

Repository

↓

Service

↓

Router
```

这是：

**对象组装流程。**

这是今天最重要的一张图。

很多初学者会把这两个方向混在一起。

其实它们完全不同。

---

# 为什么 AI Agent 项目几乎都这样设计？

因为 Agent 项目有很多共享资源。

例如：

```
LLM Client

Embedding Model

Redis

Vector Database

MCP Client

Logger

Config

Cache

Message Queue
```

这些资源不能每次请求都重新创建

否则：

- 性能差。
- 难维护。
- 难测试。

所以：

现代 AI Agent 后端几乎都会有一个**应用初始化阶段（Bootstrap）**。

启动的时候把这些资源准备好，请求的时候直接使用。

> **程序有两个生命周期。**

第一个：

```
程序启动

↓

创建整个世界
```

第二个：

```
收到请求

↓

使用这个世界
```

这是一个特别重要的世界观