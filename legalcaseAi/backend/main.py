from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router


app = FastAPI(
    title="LegalEase API",
    description="AI-Powered Legal Document Generator API",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "application": "LegalEase",
        "message": "LegalEase API is running.",
        "version": "1.0.0"
    }


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# API routes
# ---------------------------------------------------------

app.include_router(router)