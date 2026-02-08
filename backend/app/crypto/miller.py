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
    raise NotImplementedError(
        "line_function: Compute the line through P and R, evaluate at Q. "
        "Handle three cases: P≠R, P==R (tangent), P=-R (vertical). "
        "Must embed F_p coordinates into F_{p^k} for arithmetic with Q."
    )


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
    raise NotImplementedError(
        "miller: Implement Miller's algorithm using binary expansion of r. "
        "For each bit: doubling step (f = f² * line(T,T,Q), T = 2T), "
        "then if bit=1: addition step (f = f * line(T,P,Q), T = T+P). "
        "Return the accumulated f value."
    )
