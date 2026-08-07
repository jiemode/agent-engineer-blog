---
title: Service-服务层
description: 所有业务都在这一层做
---
# service.chat()为什么要加个service？

经过前面文章的历练

现在我们尝试写一个聊天接口

你可能会写：

```
@router.post("/chat")
async def chat(
    req: ChatRequest,
    service=Depends(get_chat_service)
):

    return await service.chat(req)
```

是不是已经很漂亮？

但是你有没有想过为什么：

```
service.chat(...)
```

而不是：

```
agent.chat(...)
```

为什么还要多出来Service？

之前我们说过router层只是一个传话筒，只负责接收http request，至于干实事？他才不干呢

那真正干活的人是谁？Service。

# Service是什么？

一句话:

> **业务流程的总导演。**

```
导演

↓

告诉

↓

摄影
灯光
演员
后期
音乐
```

导演自己不会拿摄影机,不会弹钢琴,不会剪视频

但是导演知道：

什么时候应该找谁

---

Service就是导演。

例如：

```
ChatService

↓

OpenAI

↓

Memory

↓

Tool

↓

Database

↓

Redis

↓

Logger
```

很相似对吧

---

# AI Agent 项目里面最重要的一层就是Service

因为真正的业务都在这里。

例如以后我们的ChatService可能长这样：

```
收到问题

↓

检查用户额度

↓

检查登录状态

↓

读取历史聊天

↓

构造Prompt

↓

调用Agent

↓

调用Tool

↓

保存Memory

↓

保存数据库

↓

返回Response
```



这里没有任何HTTP，Router，FastAPI。

Service根本不知道FastAPI存在这就是优秀架构。

---

# 那Agent负责什么？

Service负责：
```
整个业务流程
```

Agent负责：
```
推理
```

例如ChatService说：

```
用户来了。

↓

该聊天了。

↓

Agent。

交给你思考。
```

Agent开始：

```
LLM

↓

Tool

↓

Reasoning

↓

Planning
```

结束交回来

---
# 串知识时间！

结合之前的几篇文章，我们可以用一个框架来概括我们最近学到的所有东西

```
                HTTP

                  │

                  ▼

             FastAPI Router
                  │
                  ▼
         Dependency Injection
                  │
                  ▼
             ChatService
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
 ChatAgent   UserService   ToolService
     │
     ▼
 OpenAI / Claude / DeepSeek
     │
     ▼
 Repository（数据库）
     │
     ▼
 PostgreSQL / Redis
```

---
