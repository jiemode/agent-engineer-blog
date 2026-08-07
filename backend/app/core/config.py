"""全局配置。

为什么用 pydantic-settings：配置统一从 .env 读取，代码里不写死任何密钥、
端口或路径。改配置不用改代码，这也是 12-Factor 应用的原则。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agent Engineer Blog"
    database_url: str = "sqlite:///./blog.db"
    secret_key: str = "dev-secret-change-me-123456789"
    access_token_expire_minutes: int = 60

    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
