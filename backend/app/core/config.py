from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str 
    jwt_secret: str 
    env_name: str 

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        case_sensitive=False
    )  

settings = Settings()
# Now in code, use: settings.database_url instead of os.getenv()

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}

## import kagglehub; path = kagglehub.dataset_download("rabieelkharoua/predict-conversion-in-digital-marketing-dataset"); print("Path to dataset files:", path)