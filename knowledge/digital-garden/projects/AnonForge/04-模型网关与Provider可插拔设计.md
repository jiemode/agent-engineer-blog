# 模型网关与 Provider 可插拔设计

这是 AnonForge 里最值得背的架构。先看问题：

```
文本模型：OpenAI 兼容协议，POST /chat/completions
图像模型：可能走 images/generations，也可能 images/edits（multipart）
视频模型：异步任务创建 + 轮询结果，还要 AK/SK 签名
供应商：八方、可灵、魔洛、火山、通义……
```

如果每个供应商写死调用代码，系统会变成一坨 if-else。所以作者分了三层：

## 第一层：契约（core/base_provider.py）

`BaseProvider` 是所有 Provider 的基类：

```python
class BaseProvider:
    provider_key: str = ""
    model_type: str = ""

    def __init__(self, config, *, input_values=None, timeout=60.0, client=None):
        self.base_url = config.base_url
        ...

    async def generate(self, *, model_id=None, **kwargs): ...
    async def generate_stream(self, *, model_id=None, **kwargs): ...
```

子类只要实现“怎么发请求、怎么解析响应”，上层不需要知道它是谁。

## 第二层：配置即代码（app/providers/*.py）

每个供应商是一个 Python 文件，文件顶部就是配置：

```python
PROVIDER_CONFIG = {
    'key': 'bafang',
    'protocol': 'openai',
    'name': '八方中转站',
    'base_url': 'https://bafang.me/v1',
    'inputs': [{'key': 'API_KEY', 'type': 'password', 'required': True}],
    'models': [...],
}
```

为什么把配置放代码文件里而不是数据库？

- 新供应商 = 新文件，可以走 git review。
- 模板生成、AST 校验、原子写、备份都好实现。
- 敏感输入值用 `enc:v1:...` 形式加密保存。

`services/provider.py` 负责 Provider 文件的生命周期：

```
list_provider_configs → 扫描目录
create_provider_file → 用模板生成文件
update_provider_config → AST 找到 PROVIDER_CONFIG 节点并替换
_write_provider_file_atomic → 临时文件 + 原子替换 + 备份
```

## 第三层：运行时工厂（provider_runtime.py）

```python
def create_provider_for_model(model_id, *, provider_key=None, input_values=None, timeout=60.0):
    # 1. 找到包含该模型的 Provider 配置
    # 2. 根据 model_type 选实现类
    # 3. 返回实例
```

内置实现：

```
OpenAICompatibleTextProvider   文本（chat completions，含流式 SSE）
OpenAICompatibleImageProvider  图像（generations / edits）
VolcengineArkVideoProvider     视频（异步任务 + 轮询）
```

每个实现只负责“把统一请求翻译成供应商接口”，再把供应商返回收敛成统一结构。

## 统一返回：MediaGenerationOutput

图像/视频供应商返回千奇百怪，所以网关层收敛成：

```python
MediaGenerationOutput(
    data=b"",       # 原始字节
    b64="",         # base64
    url="",         # 直链
    mime_type="", width=0, height=0,
    duration_ms=0, seed="", usage={}, cost={},
)
```

业务层永远只碰这个结构。

## 总网关：ProviderModelGateway

业务层不直接调 provider_runtime，而是调网关：

```python
gateway.generate_text(model_id=..., messages=...)
gateway.generate_response(...)   # 带总超时
gateway.generate_stream(...)     # 流式
```

流式超时有个精妙设计：不是“总时长超时”，而是**块间空闲超时**：

```python
async with asyncio.timeout(self.timeout) as stream_timeout:
    async for chunk in stream(...):
        stream_timeout.reschedule(loop.time() + self.timeout)
```

只要模型还在吐字，就不掐断；卡住 60 秒才超时。这对长剧本生成特别重要。

## 和 Agent 框架的桥：ModelGatewayAdapter

deepagents / LangChain 不认识你的网关，所以又套了一层：

```
ProviderGatewayChatModel(BaseChatModel)
  → bind_tools 支持工具调用
  → _generate / _generate_stream 调用 ModelGatewayAdapter
  → adapter 调 ProviderModelGateway
```

这样 Agent 框架和供应商体系完全解耦：换模型、换供应商，Agent 代码零改动。

## 面试怎么答“多模型接入”

> “我们定义了 BaseProvider 契约和统一 MediaGenerationOutput，供应商以配置文件 + 实现类的形式热插拔；运行时按 model_id 找到 provider，再按 model_type 分派到文本/图像/视频实现；上层业务只依赖 ProviderModelGateway，不感知具体供应商。敏感 key 加密存储，文件原子替换，避免写坏供应商配置。”

这套“契约 + 配置即代码 + 工厂 + 网关”四件套，可以直接迁移到任何 AI 项目。
