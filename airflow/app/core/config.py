from pydantic import BaseSettings, AnyHttpUrl, RedisDsn


class Settings(BaseSettings):
    REDIS_URL: RedisDsn

    PROVIDER_A_URL: AnyHttpUrl
    PROVIDER_B_URL: AnyHttpUrl

    class Config:
        env_file = "./.env"


settings = Settings()
