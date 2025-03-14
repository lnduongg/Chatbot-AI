import os
from dotenv import load_dotenv
load_dotenv()


class Settings:
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_SSLMODE = os.getenv("DB_SSLMODE")
    DATABASE_URL: str = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={DB_SSLMODE}"

    API_KEY: str = os.getenv("OPENAI_KEY")
    MODEL: str = os.getenv("MODEL")

settings = Settings()