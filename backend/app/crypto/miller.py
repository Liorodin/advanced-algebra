"""Miller's algorithm for computing the Tate pairing.

The reduced Tate pairing e_r(P, Q) is computed as:
    e_r(P, Q) = f_{r,P}(Q) ^ ((p^k - 1) / r)

where f_{r,P} is the Miller function — a rational function on the curve
with divisor r[P] - r[O].

Miller's algorithm builds f_{r,P} iteratively using the binary expansion
of r, evaluating line functions at Q along the way.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.crypto.elliptic_curve import ECPoint
    from app.crypto.ext_curve import ExtCurvePoint
    from app.crypto.extension_field import ExtFieldElement


def line_function(
    P: ECPoint,
    R: ECPoint,
    Q: ExtCurvePoint,
) -> ExtFieldElement:
    """Evaluate the line through P and R at the point Q.

    Three cases:
    1. P ≠ R (distinct points): Line through P and R.
       λ = (y_R - y_P) / (x_R - x_P)
       Result: (y_Q - y_P) - λ * (x_Q - x_P)

    2. P == R (tangent line / point doubling):
       λ = (3x_P² + A) / (2y_P)
       Result: (y_Q - y_P) - λ * (x_Q - x_P)

    3. P = -R (vertical line):
       Result: x_Q - x_P

    The coordinates of P and R are in F_p, but Q's coordinates are in F_{p^k}.
    The result must be computed in F_{p^k}.

    Note: P and R coordinates must be embedded into the extension field
    before performing arithmetic with Q's coordinates.

    Args:
        P: First point (ECPoint with F_p coordinates).
        R: Second point (ECPoint with F_p coordinates).
        Q: Evaluation point (ExtCurvePoint with F_{p^k} coordinates).

    Returns:
        ExtFieldElement — the value of the line function at Q.
    """
    ext_field = Q.ext_field
    
    # Handle infinity cases
    if P.is_infinity or R.is_infinity:
        # Return 1 (identity in multiplicative group)
        from app.crypto.polynomial import Polynomial
        return ext_field.element([1])
    
    # Embed P and R coordinates into extension field
    x_P = ext_field.element([P.x.value])
    y_P = ext_field.element([P.y.value])
    x_R = ext_field.element([R.x.value])
    y_R = ext_field.element([R.y.value])
    
    # Case 3: P = -R (vertical line)
    if P.x == R.x and P.y != R.y:
        # Vertical line: x - x_P
        return Q.x - x_P
    
    # Cases 1 and 2: Need to compute slope λ
    if P == R:
        # Case 2: Tangent line (doubling)
        # λ = (3x_P² + A) / (2y_P)
        A_ext = ext_field.element([P.curve.A.value])
        three = ext_field.element([3])
        two = ext_field.element([2])
        numerator = three * (x_P ** 2) + A_ext
        denominator = two * y_P
    else:
        # Case 1: Line through distinct points
        # λ = (y_R - y_P) / (x_R - x_P)
        numerator = y_R - y_P
        denominator = x_R - x_P
    
    # Check for vertical line (denominator = 0)
    zero = ext_field.element([0])
    if denominator == zero:
        return Q.x - x_P
    
    lam = numerator / denominator
    
    # Line equation: y - y_P - λ(x - x_P) = 0
    # Evaluate at Q: (y_Q - y_P) - λ * (x_Q - x_P)
    result = (Q.y - y_P) - lam * (Q.x - x_P)
    
    return result


def vertical_line(R: ECPoint, Q: ExtCurvePoint) -> ExtFieldElement:
    """Evaluate the vertical line through R at the point Q.
    
    The vertical line through R = (x_R, y_R) is: x = x_R
    Evaluated at Q = (x_Q, y_Q): x_Q - x_R
    
    Args:
        R: Point defining the vertical line (ECPoint with F_p coordinates).
        Q: Evaluation point (ExtCurvePoint with F_{p^k} coordinates).
    
    Returns:
        ExtFieldElement — the value (x_Q - x_R).
    """
    ext_field = Q.ext_field
    
    # Handle infinity
    if R.is_infinity:
        return ext_field.element([1])
    
    # Embed R.x into extension field
    x_R = ext_field.element([R.x.value])
    
    return Q.x - x_R


def miller(
    P: ECPoint,
    Q: ExtCurvePoint,
    r: int,
) -> ExtFieldElement:
    """Miller's algorithm — compute f_{r,P}(Q).

    Algorithm (using binary expansion of r):
    1. Let r = (r_{n-1}, r_{n-2}, ..., r_1, r_0)_2 be the binary representation.
    2. Initialize: T = P, f = 1.
    3. For i from n-2 down to 0:
       a. f = f² · ℓ_{T,T}(Q) / v_{2T}(Q)    [doubling step]
       b. T = 2T
       c. If r_i == 1:
          f = f · ℓ_{T,P}(Q) / v_{T+P}(Q)     [addition step]
          T = T + P

    Here ℓ_{T,T}(Q) is the tangent line at T evaluated at Q,
    ℓ_{T,P}(Q) is the line through T and P evaluated at Q,
    and v_{2T}(Q) is the vertical line at 2T evaluated at Q.

    Note: In the reduced Tate pairing, the vertical line contributions
    cancel out in the final exponentiation, so they can often be omitted.
    For correctness and simplicity in this implementation, you may skip
    the vertical line denominators.

    Args:
        P: The first pairing argument (ECPoint in E(F_p)).
        Q: The second pairing argument (ExtCurvePoint in E(F_{p^k})).
        r: The subgroup order.

    Returns:
        ExtFieldElement f_{r,P}(Q) — the Miller function value.
    """
    ext_field = Q.ext_field
    
    # Handle edge case
    if P.is_infinity:
        return ext_field.element([1])
    
    # Get binary representation of r (as a list of bits from MSB to LSB)
    r_bits = []
    temp_r = r
    while temp_r > 0:
        r_bits.append(temp_r & 1)
        temp_r >>= 1
    r_bits.reverse()  # Now MSB first
    
    # Initialize with T = P, f = 1 (this accounts for the MSB which is always 1)
    T = P
    f = ext_field.element([1])
    
    # Process remaining bits from second-most significant to least significant
    for i in range(1, len(r_bits)):
        # Doubling step
        doubled_T = T + T
        line_val = line_function(T, T, Q)
        vert_val = vertical_line(doubled_T, Q)
        
        # Check for degenerate case (Q on vertical line)
        zero = ext_field.element([0])
        if vert_val == zero:
            # Pairing is degenerate; return 1 (or could return 0)
            return ext_field.element([1])
        
        f = (f ** 2) * line_val / vert_val
        T = doubled_T
        
        # Addition step (if bit is 1)
        if r_bits[i] == 1:
            added_T = T + P
            line_val = line_function(T, P, Q)
            vert_val = vertical_line(added_T, Q)
            
            # Check for degenerate case
            if vert_val == zero:
                return ext_field.element([1])
            
            f = f * line_val / vert_val
            T = added_T
    
    return f
