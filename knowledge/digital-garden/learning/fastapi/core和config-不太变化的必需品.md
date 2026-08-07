## Config真正负责什么？(config.py一般写在core里面)

一句话。

> **整个系统"不会因为业务改变而改变"的东西。**

什么意思？

例如：

API Key。

数据库地址。

Redis地址。

模型名称。

日志等级。

......

整个系统都需要它们，

所以应该集中管理

# 举一个AI Agent项目的真实例子

以后我们的：

```
.env
```

可能长这样

```
OPENAI_API_KEY=xxxxx

OPENAI_BASE_URL=https://api.openai.com

MODEL_NAME=gpt-4.1

DATABASE_URL=postgresql://...

REDIS_URL=redis://...

LOG_LEVEL=INFO
```

**这些都是整个系统的刚需**

---

于是。

Github上的项目都会：

```
config/
```

里面：

```
settings.py
```

例如：

```
class Settings(BaseSettings):

    openai_api_key: str

    database_url: str

    redis_url: str
```

没错，这里的BaseSettings类也是pydantic的重要成员之一

# 为什么不用到处 os.getenv()？

为什么不：

```
import os

key = os.getenv(...)
```

然后每个文件：

```
os.getenv()

os.getenv()

os.getenv()
```

结果给API Key改个名字要全项目搜索

---

真正的大项目只有：

```
settings.openai_api_key
```

改一个地方就结束

---
# 第一性原理

其实Settings 就是整个 Backend 与外部世界之间的一张配置清单

例如：

```
Backend

↓

需要知道：

OpenAI 在哪？

数据库在哪？

Redis 在哪？

JWT 密钥是什么？
```

这些全部来自Settings

---

# 那为什么不用 JSON？

很多新手会想到：

```
{
  "database": "...",
  "redis": "...",
  "api_key": "..."
}
```

为什么不用？

因为API Key不能上传 GitHub

所以整个软件行业几乎统一采用：

> **环境变量（Environment Variables）**

例如：

`.env`

```
OPENAI_API_KEY=sk-xxxx

DATABASE_URL=postgresql://...

REDIS_URL=redis://...

JWT_SECRET=abc123
```

这个文件

**永远不会上传 GitHub。**

---

# 那 Settings 在干嘛？

它只是把：

```
.env
```

里面的数据变成：

Python 对象。

例如：

```
settings.OPENAI_API_KEY
```

---

# 所以Settings其实就是一个翻译官

```
.env

↓

Settings

↓

Python对象

↓

整个项目
```

# 这其实体现了一个更大的思想


> **Single Source of Truth**

简称SSOT

> **唯一可信来源。**

以后整个项目API Key只存在于一个地方

数据库地址存在于一个地方

Redis存在于一个地方

为什么？因为：

**真相只有一个** 👀

---
# 那 Core 又是什么？

这是很多人最困惑的目录。

Github项目里几乎都会有：

```
core/
```

里面：

```
database.py

security.py

logging.py

middleware.py

lifespan.py
```


Core其实就是

> **整个系统运行所依赖的基础设施（Infrastructure）。**

🏢

假设有一栋办公楼。

---

办公楼里面有：

```
电

水

空调

电梯

网络
```

员工每天都在办公

但是几乎没人关心电梯怎么运行


---

软件也是一样。

Chat，Workflow，User每天都在工作，但是它们根本不用关心：

数据库怎么连接，日志怎么写，JWT怎么验证。

因为Core已经准备好了

---

# 所以Core里面一般放什么？

例如：

数据库连接。

```
core/

database.py
```

JWT

```
core/

security.py
```

日志

```
core/

logging.py
```

程序启动

```
core/

lifespan.py
```

异常处理

```
core/

exceptions.py
```

这些有一个共同特点

> **不是业务**

---

# 我们终于可以完整理解整个项目了。


AI Agent Backend 

```
                    Application

                           │

        ┌──────────────────┴──────────────────┐

        ▼                                     ▼

     config/                               core/

 Settings                           Database

 .env                               Logger

 API Key                            JWT

 URL                                Redis

                                    Lifespan

        │                                     │

        └──────────────────┬──────────────────┘

                           ▼

                       Router

                           ▼

                      Service

                           ▼

                       Agent

                           ▼

                    Repository

                           ▼

                       Database
```


> **优秀的软件架构，本质上不是把代码分成很多文件。**

而是：

> **把变化快的东西，和变化慢的东西，隔离开。**

我们来看几个例子：

|会经常变化|放哪里|
|---|---|
|聊天业务|`services/`|
|Agent逻辑|`agents/`|
|Prompt|`prompts/`|
|Tool|`tools/`|

而这些几乎不会天天改：

|很少变化|放哪里|
|---|---|
|数据库连接|`core/`|
|JWT|`core/`|
|日志|`core/`|
|环境变量|`config/`|

这不是在整理文件。

这是在**隔离变化（Separate Things That Change）**

而**隔离变化**，正是软件架构最核心的目标之一