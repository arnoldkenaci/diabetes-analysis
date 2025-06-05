from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Dataset Analysis API",
    description="API for automated dataset analysis and insights generation",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Dataset Analysis API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
