from fastapi import FastAPI, HTTPException
import os

app = FastAPI()

#Auth
@app.post("/auth/register")
async def create_register():
    return

@app.post("/auth/login")
async def create_login():
    return

@app.get("/me")
async def read_me():
    return

#Experiments
@app.post("/experiments")
async def create_experiemnts():
    return

@app.get("/experiments")
async def read_experiments():
    return

@app.get("/experiments/{experiment_id}")
async def read_expID(experiment_id):
    return {"experiment_id": experiment_id}

@app.patch("/experiments/{experiment_id}")
async def patch_expID(experiment_id):
    return {"experiment_id": experiment_id}

@app.delete("/experiments/{experiment_id}")
async def delete_expID(experiment_id):
    return {"experiment_id": experiment_id}

# Health check
@app.get("/health", status_code=200)
async def health_check():
    is_healthy = True
    if not is_healthy:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    environment = os.environ.get("ENV_NAME", "development")
    return {
        "status": "healthy",
         "environment": environment
    }
