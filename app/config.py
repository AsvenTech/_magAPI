from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    DB_HOST: str  
    DB_NAME: str  
    DB_USER: str  
    DB_PASSWORD: str 
    MAIL_USERNAME: str
    MAIL_PASSWORD: str 
    MAIL_FROM: str
    SENTRY_DSN: str

    class Config:
        env_file = ".env"

settings = Settings()