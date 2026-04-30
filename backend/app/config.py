from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    NEO4J_URI: str = "neo4j+s://xxxxxxxx.databases.neo4j.io"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "your-password"
    NEO4J_DATABASE: str = "neo4j"

    class Config:
        env_file = ".env"

settings = Settings()
