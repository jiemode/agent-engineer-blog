# 1. SQLModel 是什么？

先回忆一下 FastAPI。

我们之前学：

```
from pydantic import BaseModel
```

然后：

```
class Item(BaseModel):
    name: str
    price: float
```

这个东西负责：

> API 数据验证。

比如：

客户端发送：

```
{
    "name":"Keyboard",
    "price":99
}
```

FastAPI 会检查：

- name 是不是字符串？
- price 是不是数字？

---

但是。

它有一个问题：

它不会帮你存数据库。

比如：

```
item = Item(
    name="Keyboard",
    price=99
)
```

程序结束。

没了。

因为：

它只是 Python 对象。

---

于是：

我们需要：

数据库模型。

传统方式：

```
Pydantic Model

负责 API


SQLAlchemy Model

负责数据库
```

两个类。

---

例如：

```
class User(BaseModel):
    name: str
```

然后：

```
class UserTable:
    id
    name
```

同一个 User。

写两遍。

很痛苦。

🤣

---

于是：

SQLModel 出现。

它的目标：

> **让一个模型，同时服务 API 和数据库。**

---

# 2. SQLModel 的核心思想

看：

```
from sqlmodel import SQLModel, Field


class Knowledge(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str
```

这一段。

实际上包含三个世界：

---

## 世界 1：Python 类

```
class Knowledge:
```

它就是普通 Python 类。

所以：

你可以：

```
knowledge.title
```

访问属性。

---

## 世界 2：数据库表

关键：

```
table=True
```

它告诉 SQLModel：

> 我要把这个类映射成数据库表。

于是：

生成：

```
knowledge table
```

---

## 世界 3：Pydantic 数据验证

因为：

```
SQLModel
```

继承：

```
Pydantic
```

所以：

它也能验证数据。

---

所以：

一个类：

同时拥有：

```
Python对象能力

+

API验证能力

+

数据库映射能力
```

这就是 SQLModel 的魅力。

---

# 3. 为什么 id 写成这样？

你会看到：

```
id: int | None = Field(
    default=None,
    primary_key=True
)
```

第一次看：

很懵。

拆开。

---

## 第一部分

```
id: int
```

表示：

id 是整数。

---

## 第二部分

```
| None
```

表示：

允许为空。

为什么？

因为：

创建数据的时候：

我们还没有 id。

例如：

你创建：

```
Knowledge(
    title="FastAPI异步",
    content="..."
)
```

你没有写：

```
id=1
```

数据库会自动生成
所以：

创建前：

```
id=None
```

保存后：

```
id=1
```

---

## 第三部分

```
primary_key=True
```

表示：

这是主键。

数据库知道：

每一条 Knowledge 都靠它区分。