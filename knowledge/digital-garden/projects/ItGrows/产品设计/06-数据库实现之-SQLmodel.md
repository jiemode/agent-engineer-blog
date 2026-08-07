# 我们开始设计 It Grows 第一个实体

还记得吗？

🌱 Knowledge

---

第一版：

```
class Knowledge(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True
    )

    title: str

    content: str

    created_at: datetime
```

这就是：

数据库里面：

```
knowledge
```

---

对应：

现实世界：

```
一篇知识
```