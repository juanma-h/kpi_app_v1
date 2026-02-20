from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.shifts import router as shifts_router

app = FastAPI(title="KPI E-commerce Monitor API", version="0.1.0")

app.include_router(auth_router)
app.include_router(shifts_router)

@app.get("/health")
def health():
    return {"status": "ok"}
