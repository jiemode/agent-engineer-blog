---
title: lifespan 与 asynccontextmanager 详解
description: 从 @asynccontextmanager 出发，看懂 FastAPI 的启动与关闭
---

# lifespan 与 asynccontextmanager 详解

这是我做 `agent_engineer` 博客项目时补的一课。当时看到 `main.py` 里：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
```

第一反应是：这是什么魔法？拆开之后发现，它一点都不神秘。

## 1. @ 装饰器是什么

Python 里：

```python
@asynccontextmanager
async def lifespan(app): ...
```

等价于：

```python
async def lifespan(app): ...
lifespan = asynccontextmanager(lifespan)
```

装饰器就是“给函数换一件衣服”，把我们写的函数包装成另一个对象。

## 2. 什么是上下文管理器

你其实早就写过上下文管理器了，就是 `with`：

```python
with open("file.txt", "w") as f:
    f.write("hello")
```

`with` 帮你做了两件事：进入时打开文件，退出时自动关闭。

所以上下文管理器 = **一段代码的进入和退出都有人管理**。

## 3. asynccontextmanager 就是异步版的这个工具

它把一个“含 `yield` 的异步函数”变成 `async with` 能用的对象：

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def my_manager():
    print("进入：开始")
    yield
    print("退出：收尾")

async def main():
    async with my_manager():
        print("中间：干活")
```

运行顺序：

```text
进入：开始
中间：干活
退出：收尾
```

关键就是那个 `yield`：

- `yield` 上面的代码 = 进入时执行
- `yield` 下面的代码 = 退出时执行
- `yield` 让程序“暂停在这里”，等你干完活再回来收尾

## 4. 我们的 lifespan 在干什么

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
```

翻译成人话：

```text
服务器启动时：
  执行 create_db_and_tables() → 建数据库表

然后：
  yield → 程序在这里定住，开始正常处理请求

服务器关闭时：
  执行 yield 后面的代码（我们这里没有，所以什么都不做）
```

FastAPI 启动时会像 `async with lifespan(app)` 一样进入它，请求来了就在 `yield` 期间处理，服务器关闭时再退出。

## 5. 这和 get_session 是一家人

`core/database.py` 里的：

```python
def get_session():
    with Session(engine) as session:
        yield session
```

也是同一个思想：

```text
进入：打开一个数据库会话
yield：把 session 交给路由函数使用
退出：自动关闭会话
```

区别在于范围：

- `lifespan` 管理**整个应用**的生命周期
- `get_session` 管理**一次请求**的生命周期

## 6. 为什么要用 lifespan，而不是 on_event

老写法：

```python
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
```

它已经被 FastAPI 标记为过时，因为：

- 启动和关闭代码被拆到两个地方，容易漏
- 生命周期逻辑不透明
- `lifespan` 把“启动做什么、关闭做什么”放在一个函数里，一目了然

## 面试一句话总结

`@asynccontextmanager` 就是把“函数里夹着一个 yield 的异步代码”包装成“进入 → 干活 → 收尾”的生命周期工具；FastAPI 的 `lifespan` 用它来安排整个服务器的启动和关闭，`create_db_and_tables()` 在启动时跑，之后服务器就开始正常接客了。
