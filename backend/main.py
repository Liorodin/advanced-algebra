"""FastAPI application entry point for BLS Signature Scheme backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.bls import router as bls_router

app = FastAPI(
    title="BLS Signature Scheme",
    description="BLS Cryptographic Signature using Reduced Tate Pairing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bls_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
