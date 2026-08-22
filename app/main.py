from fastapi import FastAPI
from app.api.flag_routes import router

app = FastAPI(
    title="Feature Flag Management System",
    version="1.0.0",
)
@app.get("/")

def home():
    return {"message": "Feature flag management system is running" }

app.include_router(router)