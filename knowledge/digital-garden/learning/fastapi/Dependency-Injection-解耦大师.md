# 为什么需要依赖注入？

假设我们写聊天

很多新人会写：

```
@app.post("/chat")
async def chat():

    client = OpenAI()

    redis = Redis()

    db = Database()

    ...
```

写了一个接口，感觉没问题...

但是如果整个项目有100个API会发生什么？

->要重复写100个
```
 OpenAI()

OpenAI()

OpenAI()

OpenAI()

Database()

Database()

Redis()

Redis()

Redis()

    ...
```
已爆炸(T-T)

## 真正的问题是什么？

> 重复代码？

其实不是。

真正的问题是：

> **耦合(Coupling)。**

什么意思？

你的 Router。

现在知道：

- 怎么创建数据库
- 怎么创建 Redis
- 怎么创建 OpenAI Client

也就是说Router开始负责：
**创建对象**

但是...

> **Router 只负责接收 HTTP 请求**

Router 就像服务员

它应该说有客人点了一份宫保鸡丁然后把订单交给厨房

至于：

鸡肉哪里来？

锅哪里来？

油哪里来？

不是服务员负责

所以：

现在Router 已经开始"兼职"了,这就是耦合（耦合 $\approx$ 兼职）

## 然后Depends() 出现了

既然 Router 不应该创建这些对象...

那fastapi帮你准备（用依赖注入）

于是就有诸如：

```
def get_db():

    return Database()
```
```
def get_openai():

    return OpenAI()
```

然后Router变成：

```
@app.post("/chat")
async def chat(

    db = Depends(get_db),

    client = Depends(get_openai)

):
```

Router甚至不知道Database 怎么来的。

它只知道：

> 有人会给我。

这就是Dependency Injection。

一句话：

> **不要自己创建，而是让别人提供。**

> **一个模块应该声明"我需要什么（What I Need）"，而不是决定"我要如何创建它（How to Create It）"**

这是依赖注入真正的价值
