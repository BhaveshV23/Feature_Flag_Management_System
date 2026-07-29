from fastapi import FastAPI

app = FastAPI()
@app.get("/")

def home():
    return {"message": "Feature flag management system is running" }