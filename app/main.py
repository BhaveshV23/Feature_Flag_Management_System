from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.flag_routes import router as flags_router
from app.api.auth import router as auth_router
from app.api.audit_routes import router as audit_router

app = FastAPI(
    title="Feature Flag Management System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")

def home():
    return {"message": "Feature flag management system is running" }

app.include_router(flags_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
