# Pydantic 和 BaseModel：给数据立规矩

我第一次看到 `from pydantic import BaseModel` 也是一头雾水。这一篇用最直白的话把 Pydantic 讲清楚，并且把和 AI Agent 面试强相关的部分放在最前面。

## Pydantic 到底是干嘛的

一句话：**Pydantic 是给数据立规矩、查规矩、转换格式的库。**

它做三件事：

1. 校验：数据不符合规则就拒绝，并给出错误信息。
2. 转换：把字符串、字典等“外来数据”自动变成 Python 类型。
3. 序列化：把 Python 对象变成 JSON 字典，方便返回给前端或传给大模型。

而 `BaseModel` 就是“规矩模板”：

```python
from pydantic import BaseModel

class BlogPost(BaseModel):
    title: str
    content: str
    tags: list[str] = []
```

这声明了一份博客文章的规矩：

- 必须有 `title`，而且必须是字符串
- 必须有 `content`，而且必须是字符串
- `tags` 可以没有，默认给一个空列表

可以把它理解成一张海关申报单：`BaseModel` 是空白申报单，Pydantic 是海关检查员，数据是要申报的物品。物品不符合申报单，直接拦下（422）；符合，才放行进入业务逻辑。

## 五个必会操作

```python
from pydantic import BaseModel, Field

class BlogPost(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str
    tags: list[str] = []
    published: bool = False

# 1. 从字典创建对象（最常用：请求体、LLM 返回的 JSON）
post = BlogPost.model_validate({
    "title": "我学会了 Pydantic",
    "content": "正文",
    "tags": ["python", "agent"],
})
print(post.title)

# 2. 从 JSON 字符串创建对象（最常用：解析大模型输出）
json_text = '{"title": "test", "content": "hi"}'
post2 = BlogPost.model_validate_json(json_text)

# 3. 自动转换类型（字符串变整数，很强大）
class Chapter(BaseModel):
    chapter_no: int

chapter = Chapter.model_validate({"chapter_no": "12"})  # "12" 自动变 12

# 4. 转回字典 / JSON（给前端、给 LLM）
data = post.model_dump()          # dict
json_data = post.model_dump_json()  # JSON 字符串

# 5. 校验失败会怎样
try:
    BlogPost.model_validate({"title": 123, "content": "hi"})
except Exception as exc:
    print(exc)  # 你会看到 title 必须是字符串的详细报错
```

`model_validate`、`model_dump` 这两个方法是 Pydantic v2 里必背的 API，面试也常考。

## 嵌套模型：真实项目里到处是这个

一个博客系统不会只有一层，真实结构是“对象套对象”：

```python
class Author(BaseModel):
    name: str

class BlogPost(BaseModel):
    title: str
    author: Author          # 嵌套另一个 BaseModel
    related: list["BlogPost"] = []   # 甚至可以套自己
```

大模型返回一段包含人物、事件、设定的 JSON 时，就是用这种嵌套模型一次校验整棵结构。真实项目里的 `MediaGenerationOutput`、`ScreenwritingRagHit`、`ProviderConfig` 全是同一套思路：**用一个 Pydantic 模型给外部世界的复杂数据定一份可校验、可序列化的契约。**

## 为什么 AI Agent 工程师必须吃透它

### 1. LLM 输出结构化管理

大模型返回的永远是一串文本，但业务需要稳定的 JSON。正确做法是：

```python
class ChapterEvent(BaseModel):
    chapter_index: int
    title: str
    event_summary: str

try:
    event = ChapterEvent.model_validate_json(llm_raw_output)
except Exception:
    # 解析失败就重试一次，或把错误信息回传给模型让它修正
    event = ChapterEvent.model_validate_json(retry_with_error_message(llm_raw_output))
```

这就是“LLM 结构化输出 + 失败重试”的最小实现，也是 RAG、事件清洗、Agent 工具调用里的核心模式。

### 2. Agent 工具的参数契约

Agent 要调用 `get_rag_context`、`get_novel_events` 这类工具时，工具参数通常也用 Pydantic 定义。好处是：大模型生成什么参数、工具真正收什么参数，完全对齐，不会被脏数据打进业务层。

### 3. 前后端与多服务之间的数据契约

Pydantic 模型同时承担“请求校验”和“响应序列化”。FastAPI 里写：

```python
@app.post("/api/posts", response_model=BlogPost)
def create_post(post: BlogPost):
    return post
```

`response_model` 会保证返回给前端的东西一定符合 `BlogPost` 的结构：多返回的字段会被过滤，缺字段会报错。这在分层架构里是“边界守门员”。

## 面试高频题与答题模板

### Pydantic 和 dataclass 有什么区别？

> dataclass 只负责减少样板代码，不自动做数据校验和类型转换；Pydantic 在类型注解之上实现了运行时校验、自动转换、序列化，还支持嵌套模型、字段约束、validator，并且被 FastAPI、SQLModel、LangChain 等生态直接集成。

### 怎么把数据库 ORM 对象转成 Pydantic 模型？

> 在模型上配置 `model_config = ConfigDict(from_attributes=True)`，然后用 `Model.model_validate(orm_obj)`。这也是项目里 models 和 schemas 分离的原因：数据库表存全部字段，API 只暴露需要的字段。

### Pydantic v1 和 v2 最大的区别？

> v2 底层用 Rust 写的 pydantic-core，性能大幅提升；API 从 `.dict()` 改为 `.model_dump()`，从 `parse_obj` 改为 `model_validate`，validator 改为 `field_validator/model_validator`。

### 如何校验一段 LLM 返回的 JSON？

> 用 `Model.model_validate_json(raw)`，失败时捕获异常，把错误信息拼进重试提示词，或降级到规则解析。必要时先 `json.loads` 再做清洗，因为模型经常在 JSON 外面包 Markdown 代码块。

## 给你的作业

在 FastAPI 的 `main.py` 里加一个小实验：

```python
@app.get("/api/posts/demo")
def demo_post():
    raw = '{"title": "大模型给的标题", "content": "内容", "tags": ["agent"]}'
    post = BlogPost.model_validate_json(raw)
    return post.model_dump()
```

然后故意改错 JSON，比如把 `tags` 写成 `"tags": "agent"`，看看返回什么。你会在报错信息里看到 Pydantic 告诉你：字符串不能当作列表。**能读懂报错信息，比背概念更能证明你学会了。**

## 一句话记忆

**BaseModel 是合同模板，Pydantic 是法务，FastAPI 是前台；任何数据进门之前，先过法务这一关。**
