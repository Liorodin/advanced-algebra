"""Pydantic models for BLS API request and response validation."""

from pydantic import BaseModel, Field


class PointResponse(BaseModel):
    """Representation of an elliptic curve point."""
    x: str
    y: str


class BLSRequest(BaseModel):
    """Request schema for the BLS signature pipeline.

    Attributes:
        p: Prime field characteristic. Must be prime and ≡ 3 (mod 4).
        A: Elliptic curve coefficient A.
        B: Elliptic curve coefficient B.
        private_key: Secret key integer a.
        message: Message string to sign.
    """
    p: int = Field(..., description="Prime field characteristic (must be prime, p ≡ 3 mod 4)")
    A: int = Field(..., description="Elliptic curve coefficient A")
    B: int = Field(..., description="Elliptic curve coefficient B")
    private_key: int = Field(..., description="Private key (secret integer a)")
    message: str = Field(..., description="Message to sign")


class BLSResponse(BaseModel):
    """Response schema for the BLS signature pipeline.

    Contains all intermediate computation results for step-by-step display.
    """
    group_order: int = Field(..., description="|E(F_p)| — number of points on the curve")
    r: int = Field(..., description="Largest prime factor of group order")
    cofactor: int = Field(..., description="|G| / r")
    embedding_degree: int = Field(..., description="Smallest k where r | p^k - 1")
    irreducible_poly: str = Field(..., description="Irreducible polynomial f(x) for F_{p^k}")
    hash_point: PointResponse = Field(..., description="H(m) — message hashed to curve point")
    signature: PointResponse = Field(..., description="sig = a * H(m)")
    Q: PointResponse = Field(..., description="Public point in E(F_{p^k})")
    pairing_lhs: str = Field(..., description="e_r(sig, Q) — left side of verification")
    pairing_rhs: str = Field(..., description="e_r(H(m), aQ) — right side of verification")
    verified: bool = Field(..., description="Whether the signature verification passed")
    display_message: str = Field(..., description="Human-readable verification result")
