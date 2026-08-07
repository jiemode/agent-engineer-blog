# python -m venv：命令行、模块与对象

这节课的来源是一次诚实的“翻车”：我以为 `python -m venv .venv` 里的 `-m` 是“开启名字自定义功能”。老师点评：前半句对，后半句错，并帮我拆开了三个必须补的底层概念。

## 一行命令拆成三块

```text
python   -m   venv   .venv
 程序   选项   参数1   参数2
```

- `python`：要运行的程序；
- `-m`：python 的选项，意思是“按模块方式运行”；
- `venv`：Python 内置模块的名字；
- `.venv`：传给 `venv` 模块的参数，决定虚拟环境文件夹的名字。

大白话翻译：**Python，请运行 `venv` 这个模块，把环境建到 `.venv` 文件夹里。**

`-m` 和“能不能自定义名字”无关。把参数改成 `my_env`，环境就叫 `my_env`。

## 三个必须记住的底层模型

### 1. 命令行 = 程序 + 选项 + 参数

读任何命令第一件事都是拆这三块。以后遇到 `uvicorn main:app --reload`、`pytest -q`、`alembic upgrade head`，都是在同一套结构里变化。

### 2. python -m 模块名 = 按 import 方式运行

Python 有两条运行路径：

```text
python my_script.py        # 按文件路径运行
python -m my_module        # 按模块名运行，复用 import 查找机制
```

AI Agent 项目里大量命令都是第二种，例如：

```text
python -m uvicorn app.main:app
python -m pytest
python -m app.services.novel_browser_proxy
```

### 3. uvicorn main:app = 模块:对象

```text
main = main.py 这个模块
app  = main.py 里的 app 对象（FastAPI 实例）
```

`app` 不是类，是对象。

## 类 vs 对象：图纸 vs 机器

```python
class FastAPI: ...      # 图纸（类）
app = FastAPI(...)      # 按图纸造出来的机器（对象）
```

AnonForge 的真实写法：

```python
def create_app() -> FastAPI:
    app = FastAPI(...)
    return app

app = create_app()
```

`uvicorn main:app` 要的是那台机器，不是图纸。

## 为什么 AI Agent 工程师必须懂

后面会大量看到这种代码：

```python
class BaseProvider:      # 类（图纸）
    ...

provider = OpenAICompatibleTextProvider(config)  # 对象（机器）
```

能随口说出“这是类还是对象”，面试时聊架构会非常扎实。

## 复习题

1. `python -m venv my_env` 创建的环境叫什么名字？
2. `-m` 是谁的选项？它的作用是什么？
3. 用一句话解释 `uvicorn main:app` 里的 `main` 和 `app`。