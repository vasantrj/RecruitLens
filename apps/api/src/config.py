from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RecruitLens"
    environment: str = "development"
    database_url: str
    groq_api_key: str = ""

    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"

    github_token: str = ""

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/integrations/gmail/callback"

    jwt_secret_key: str = "change-this-to-a-random-secret-in-production"

    class Config:
        env_file = ".env"


settings = Settings()