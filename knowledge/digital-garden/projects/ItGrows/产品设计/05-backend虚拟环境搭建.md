# 第一步：为什么需要虚拟环境？

> 我电脑不是已经装 Python 了吗？

确实装了，但是假设一年以后

你的电脑里面有：

```
it grows
AI Resume
Workflow Agent
RAG Demo
LangGraph Playground
```

五个项目

第一个项目：

```
fastapi==0.120
```

第二个项目：

```
fastapi==0.118
```

第三个项目：

```
pydantic==1
```

第四个项目：

```
pydantic==2
```

如果全部安装到：

```
C:\Python\
```

世界大战开始了

---

所以Python 发明了：

## Virtual Environment

它其实就是：

> **每个项目自己的 Python 小房间。**

例如：

```
电脑

├── Project A
│      └── .venv/
│
├── Project B
│      └── .venv/
│
└── Project C
       └── .venv/
```

大家互不打扰。

---

# 第二步：为什么我们选择 uv？


以前用pip：

```
python -m venv .venv
pip install ...
pip freeze > requirements.txt
```

命令一大堆。

现代 Python：

```
uv venv
uv add fastapi
```

结束

这也是很多新项目采用的方式。

---

# 第三步：真正建立 Runtime

进入：

```
backend/
```

执行：

```
uv venv
```

会生成：

```
backend/

├── .venv/
```


然后在终端PowerShell：

```
.venv\Scripts\Activate.ps1
```

如果成功。

终端前面会出现：

```
(.venv)
```

---

# 第四步：安装依赖



先进行初始化：
```
uv init
```

`uv init` 的作用就是：

> **创建一个标准 Python 项目。**

它会帮你生成：

```
backend/

├── pyproject.toml
├── README.md（可选）
├── .python-version
```

里面最重要的是pyproject.toml：

```
[project]
name = "backend"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = []
```

有了它以后：

```
uv add fastapi uvicorn pydantic-settings
```

才能成功

---

# 不过……

CTO 要告诉你一个更现代的方式。

其实现在很多团队都是这样开始项目：

```
uv init
```

↓

```
uv venv
```

↓

```
uv add fastapi
```

↓

开始开发
我们只装最核心的几个

```
uv add fastapi uvicorn pydantic-settings
```

这三个够了。

安装完成以后。

你会发现：

```
backend/

├── pyproject.toml
├── uv.lock
└── .venv/
```

有没有发现？

**我们没有写 requirements.txt。**

因为：

`uv add`

已经自动维护依赖了。

---

# 第五步：pyproject.toml

打开它。

你会发现类似：

```
[project]
name = "backend"
version = "0.1.0"

dependencies = [
    "fastapi",
    "uvicorn",
    "pydantic-settings"
]
```

这就是：

> **项目身份证。**

以后：

作者是谁？

Python 版本？

依赖？

都会放这里。

---

# 第六步：终于运行！

执行：

```
uv run uvicorn app.main:app --reload
```

注意：

不是：

```
python main.py
```

为什么？

因为：

FastAPI 本质上不是一个普通 Python 程序。

它需要：

> **ASGI Server（Uvicorn）**

来托管。

这里你会突然发现，我们以前学的：

```
app = FastAPI()
```

原来一直只是：

> **一辆汽车。**

而：

```
Uvicorn
```

才是：

> **发动汽车的司机。**