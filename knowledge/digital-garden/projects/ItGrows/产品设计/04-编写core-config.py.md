config.py:

```
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str = "it grows"

    API_V1_STR: str = "/api/v1"

    OPENAI_API_KEY: str = ""

    DATABASE_URL: str = ""

    REDIS_URL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
```

# 一行一行拆:

## 第一行

```
class Settings(BaseSettings):
```

BaseSettings

什么意思？

其实就是Pydantic：

> 我帮你自动去：

```
.env
```

里面找

如果没有 BaseSettings。

以后每天：

```
os.getenv(...)
```

写到哭

---

# 第二行。

```
PROJECT_NAME
```

以后整个项目都可以：

```
settings.PROJECT_NAME
```

获取

不用：

```
PROJECT_NAME = "..."
```

到处复制

---

# 最后一行。

```
settings = Settings()
```


> **创建一个全局唯一的配置对象。**

以后。

整个 Backend全部：

```
from app.core.config import settings
```