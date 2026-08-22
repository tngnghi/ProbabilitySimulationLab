from pathlib import Path
"""from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    database_url: str 
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    env_name: str = "development"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 7
    redis_url: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", 
        env_file_encoding="utf-8", 
        extra="ignore",
        case_sensitive=False
    )

settings = Settings()
# Now in code, use: settings.database_url instead of os.getenv()


"""app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}
"""
## import kagglehub; path = kagglehub.dataset_download("rabieelkharoua/predict-conversion-in-digital-marketing-dataset"); print("Path to dataset files:", path)