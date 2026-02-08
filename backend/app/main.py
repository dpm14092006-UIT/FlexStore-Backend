from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.endpoints import router
# Import models to ensure tables are created
from app.models import sql_models 
from app.database import engine
from dotenv import load_dotenv
import os

load_dotenv()

# Create Tables
sql_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlexStore 3D API", version="2.0")

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router
app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "FlexStore 3D System Ready"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)