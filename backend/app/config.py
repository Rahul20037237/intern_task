# core/config.py

from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field, ValidationError

class Settings(BaseSettings):
    HUGGING_FACE_KEY: SecretStr= Field(..., env="HUGGING_FACE_KEY")
    VECTOR_DB_PATH: str = Field(default="vector_db", env="VECTOR_DB_PATH")
    MAX_TOKENS_PER_CHUNK: int = Field(default=500, env="MAX_TOKENS_PER_CHUNK")
    MODEL_NAME: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    SUPABASE_URL:str=Field(...,env="SUPABASE_URL")
    SUPABASE_KEY:SecretStr=Field(...,enc="SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY:SecretStr=Field(...,env="SUPABASE_SERVICE_ROLE_KEY")
    BUCKET_NAME:str=Field(...,env="BUCKET_NAME")

    class Config:
        env_file =".env"
        env_file_encoding = "utf-8"

try:
    settings = Settings()
except ValidationError as e:
    print(" Environment configuration is invalid:")
    print(e.json(indent=2))
    raise SystemExit(1)

if __name__ == "__main__":
    print("Configuration loaded successfully.")
    print("Vector DB Path:", settings.VECTOR_DB_PATH)
    print("Model Name:", settings.MODEL_NAME)
