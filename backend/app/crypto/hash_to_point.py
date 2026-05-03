"""Hash-to-point: H(m) → E(F_p).

Maps an arbitrary message string to a point on the elliptic curve.
This is a critical component of BLS signatures — the message must be
represented as a curve point for the pairing to work.

Three-step process:
1. string_to_field_element: Convert message to an integer mod p.
2. increment_and_try: Find a valid x-coordinate on the curve.
3. cofactor_clear: Ensure the resulting point has order r.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.crypto.prime_field import PrimeField, FieldElement
    from app.crypto.elliptic_curve import EllipticCurve, ECPoint


def string_to_field_element(message: str, field: PrimeField) -> FieldElement:
    """Convert a message string to a field element using base-256 encoding.

    Interpret the message as a big integer by treating each byte as a
    base-256 digit:
        value = sum(byte[i] * 256^i for i in range(len(bytes)))

    Then reduce modulo p to get a field element.

    Uses UTF-8 encoding for the message bytes.

    Args:
        message: The input message string.
        field: The prime field F_p.

    Returns:
        A FieldElement representing the message.

    Example:
        "שלום" in UTF-8 → bytes → big integer → mod p
    """
   # 1. Encode message as Windows-1255 bytes per assignment instructions
    message_bytes = message.encode('windows-1255')
    
    # 2. Convert to big integer (base-256) using Big-Endian formulation
    value = 0
    n = len(message_bytes)
    for i, byte in enumerate(message_bytes):
        value += byte * (256 ** (n - 1 - i))
    
    # 3. Reduce modulo p
    return field.element(value % field.p)


def increment_and_try(x: FieldElement, curve: EllipticCurve) -> ECPoint:
    """Find a point on the curve by trying x, x+1, x+2, ... until successful.

    For each candidate x:
    1. Compute z = x³ + Ax + B.
    2. Check if z is a quadratic residue (using Euler's criterion).
    3. If yes, compute y = sqrt(z) and return (x, y).
    4. If no, try x + 1.

    Args:
        x: Starting FieldElement to try as x-coordinate.
        curve: The elliptic curve.

    Returns:
        An ECPoint on the curve.

    Raises:
        RuntimeError: If no valid point found (shouldn't happen for large enough p).
    """
    from app.crypto.elliptic_curve import ECPoint
    
    field = curve.field
    max_attempts = field.p  # Try all possibilities if needed
    
    for _ in range(max_attempts):
        # Compute z = x³ + Ax + B
        z = x**3 + curve.A * x + curve.B
        
        # Check if z is a quadratic residue
        if z.is_quadratic_residue():
            # Compute y = sqrt(z)
            # For p ≡ 3 (mod 4), y = z^((p+1)/4)
            y = z.sqrt()
            return ECPoint(curve, x, y)
        
        # Try next x
        x = x + field.element(1)
    
    raise RuntimeError(f"Could not find valid point after {max_attempts} attempts")


def cofactor_clear(point: ECPoint, group_order: int, r: int) -> ECPoint:
    """Multiply point by the cofactor |G|/r to get a point of order r.

    Since |G| = cofactor * r, multiplying any point by the cofactor
    gives a point whose order divides r.

    Args:
        point: An ECPoint on the curve.
        group_order: |E(F_p)| = |G|.
        r: The target subgroup order.

    Returns:
        An ECPoint of order dividing r (ideally exactly r).
    """
    cofactor = group_order // r
    return cofactor * point


def hash_to_point(message: str, curve: EllipticCurve, r: int) -> ECPoint:
    """Full hash-to-point pipeline: message → curve point of order r.

    Orchestrates:
    1. string_to_field_element(message, field) → x
    2. increment_and_try(x, curve) → P
    3. cofactor_clear(P, |G|, r) → H(m)

    Args:
        message: The message to hash.
        curve: The elliptic curve.
        r: The subgroup order.

    Returns:
        An ECPoint H(m) of order r on the curve.

    Example:
        For p=103, A=1, B=0, message="שלום": H(m) = (32, 47)
    """
    # Step 1: Convert message to field element
    x = string_to_field_element(message, curve.field)
    
    # Step 2: Find a point on the curve
    P_temp = increment_and_try(x, curve)
    
    # Step 3: Clear cofactor to get point of order r
    group_order = curve.group_order()
    H_m = cofactor_clear(P_temp, group_order, r)
    
    return H_m
