# 我们先不说代码

假设数据库里面有一张用户表。

```
users

id

username

email

password_hash

created_at
```

注意里面有：

```
password_hash
```

也就是密码（加密后的）。

---

现在浏览器访问：

```
GET /users/1
```

你觉得服务器应该返回什么？

应该返回这些吗：

```
{
  "id":1,
  "username":"Kyle",
  "email":"xxx@gmail.com",
  "password_hash":"$2a$12$xxxxxxxx"
}
```

当然不能！

密码哈希虽然不是明文密码，但也**绝对不应该返回给前端**。

---

# 软件工程出现了


> **数据库里的 User。**

和：

> **返回给用户看的 User。**

真的是同一个东西吗？

> **不是。**

软件工程把 User 分成了：

## 第一种。

Database Model

也就是：

```
User
```

它负责：

> **数据库。**

里面可以有：

```
password_hash

is_admin

deleted

last_login_ip
```

这些前端永远不应该知道。

---

## 第二种

Response Schema

例如：

```
UserPublic
```

里面只有：

```
id

username

email
```


# 所以Models是什么？

一句话。

> **数据库怎么看数据。**

# Schemas是什么？

一句话。

> **API 怎么看数据。**

# 为什么这件事情这么重要？

因为AI Agent 项目以后会越来越复杂

例如Knowledge数据库里面：

```
Knowledge

id

title

content

embedding

created_at

updated_at
```

等等

但是前端列表页面其实只需要：

```
title

created_at
```

Embedding 呢？

几十万个浮点数你总不能全部返回吧

---

所以Schema决定：

> **接口应该返回什么。**

不是数据库决定

---

# 那为什么还有 Request Schema？

再举一个例子注册用户

浏览器发送：

```
{
  "username":"Kyle",
  "password":"123456"
}
```

数据库里面却保存：

```
password_hash
```

有没有发现。

又不是一个东西。

于是：

```
UserCreate
```

出现了

---

所以我们能经常看到：

```
User(SQLModel)

↓

UserCreate

↓

UserUpdate

↓

UserResponse

↓

UserPublic

↓

UserAdmin
```


怎么这么多？

其实这是**职责分离**

为什么 FastAPI 社区几乎所有项目都是：

```
models/

schemas/
```

不是为了好看，而是因为：

> **数据库模型，与 API 模型，从来就不是同一个模型。**

---

# AI Agent 更明显。

假设一个Knowledge数据库：

```
title

content

embedding

chunk_size

owner_id

created_at

updated_at
```

AI真正需要的：

```
content
```

---

前端真正需要：

```
title
```

---

列表真正需要：

```
id

title
```

---

搜索真正需要：

```
score

snippet
```

所以Schema越来越多，数据库还是一个