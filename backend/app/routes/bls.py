"""API routes for BLS signature operations."""

from fastapi import APIRouter, HTTPException
from app.schemas.bls import BLSRequest, BLSResponse
from app.crypto.bls import BLSSignatureScheme

router = APIRouter(prefix="/api/bls", tags=["BLS"])


@router.post("/run", response_model=BLSResponse)
async def run_bls(request: BLSRequest) -> BLSResponse:
    """Execute the full BLS signature pipeline.

    Takes curve parameters, private key, and message. Returns all
    intermediate values and the verification result.

    Raises:
        HTTPException: 400 if parameters are invalid.
        HTTPException: 500 if a stub is not yet implemented.
    """
    try:
        scheme = BLSSignatureScheme(
            p=request.p,
            A=request.A,
            B=request.B,
            private_key=request.private_key,
        )
        steps = scheme.get_steps(request.message)
        return BLSResponse(**steps)
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail=f"Not yet implemented: {str(e)}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameters: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}",
        )
