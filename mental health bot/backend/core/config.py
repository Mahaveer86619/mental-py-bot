import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="../../.env")  # Adjust path if needed


class Settings(BaseSettings):
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "YOUR_DEFAULT_API_KEY_IF_NOT_SET")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    class Config:
        # If your .env file is in the same directory as this script, you might not need load_dotenv
        # and can use this instead:
        env_file = "../../.env"  # Adjust path if needed
        env_file_encoding = "utf-8"


settings = Settings()

# Basic validation
if (
    settings.GOOGLE_API_KEY == "YOUR_DEFAULT_API_KEY_IF_NOT_SET"
    or not settings.GOOGLE_API_KEY
):
    print("WARNING: GOOGLE_API_KEY is not set in the environment or .env file.")
if settings.SECRET_KEY == "default_secret":
    print(
        "WARNING: Using default SECRET_KEY. Please set a strong secret in your .env file."
    )
