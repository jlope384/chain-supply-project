from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    NEO4J_URI: str
    NEO4J_USER: str = Field(alias="NEO4J_USERNAME")
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str

    class Config:
        env_file = ".env"
        populate_by_name = True

settings = Settings()
