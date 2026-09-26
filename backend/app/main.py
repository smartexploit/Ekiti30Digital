from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import admin, stories, uploads

app = FastAPI(title="Ekiti30Digital Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(stories.router)
app.include_router(uploads.router)

@app.get("/")
def read_root():
    return {"message": "Ekiti30Digital Backend API is running"}
