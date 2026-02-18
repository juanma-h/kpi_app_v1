from fastapi import FastAPI
from app.routers.auth import router as auth_router

app = FastAPI(title="KPI E-commerce Monitor API", version="0.1.0")

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}
