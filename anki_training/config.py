from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
    )

    COLLECTION_PATH: str = "c:/Users/user/AppData/Roaming/Anki2/User 1/collection.anki2"
    OPEN_AI_API_KEY: str = ""


settings = Settings()
