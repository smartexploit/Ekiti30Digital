from fastapi import FastAPI
from app.api.api import api_router

app = FastAPI(title="Ekiti30 Digital API", version="1.0.0")

# Mount both directly and under /api/v1
app.include_router(api_router)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Ekiti30 Digital API is running"}
