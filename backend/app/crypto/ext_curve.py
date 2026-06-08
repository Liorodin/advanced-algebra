"""Elliptic curve points over extension fields E(F_{p^k}).

This module provides an ECPoint-like class but with coordinates in F_{p^k}
(ExtFieldElement). Needed for the second argument Q of the Tate pairing,
which must be a point in E(F_{p^k}) but not in E(F_p).
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.crypto.extension_field import ExtensionField, ExtFieldElement
    from app.crypto.elliptic_curve import EllipticCurve


class ExtCurvePoint:
    """A point on an elliptic curve with coordinates in an extension field.

    Same interface as ECPoint, but x and y are ExtFieldElement instances.
    The curve equation is still y² = x³ + Ax + B, but A and B are embedded
    into the extension field as constant polynomials.

    Attributes:
        curve: The base EllipticCurve (for A, B parameters).
        ext_field: The extension field F_{p^k}.
        x: x-coordinate as ExtFieldElement, or None if infinity.
        y: y-coordinate as ExtFieldElement, or None if infinity.
        is_infinity: True if this is the point at infinity.
    """

    def __init__(
        self,
        curve: EllipticCurve,
        ext_field: ExtensionField,
        x: ExtFieldElement | None,
        y: ExtFieldElement | None,
        is_infinity: bool = False,
    ) -> None:
        """Initialize a point on E(F_{p^k}).

        Args:
            curve: The elliptic curve (provides A, B).
            ext_field: The extension field for coordinates.
            x: x-coordinate as ExtFieldElement, or None for infinity.
            y: y-coordinate as ExtFieldElement, or None for infinity.
            is_infinity: Whether this is the point at infinity.
        """
        self.curve = curve
        self.ext_field = ext_field
        self.x = x
        self.y = y
        self.is_infinity = is_infinity

    def __add__(self, other: ExtCurvePoint) -> ExtCurvePoint:
        """Point addition on E(F_{p^k}).

        Same formulas as ECPoint.__add__, but using ExtFieldElement arithmetic.

        Args:
            other: Another ExtCurvePoint on the same curve.

        Returns:
            New ExtCurvePoint representing the sum.
        """
        if self.curve != other.curve or self.ext_field != other.ext_field:
            raise ValueError("Points must be on the same curve and extension field")
        
        # Case 1: P + O = P
        if self.is_infinity:
            return other
        if other.is_infinity:
            return self
        
        # Embed curve coefficients A into extension field
        A_ext = self.ext_field.element([self.curve.A.value])
        
        # Case 2: P + (-P) = O (same x, opposite y)
        if self.x == other.x and self.y != other.y:
            return ExtCurvePoint(self.curve, self.ext_field, None, None, is_infinity=True)
        
        # Case 3: P + P (doubling)
        if self == other:
            zero = self.ext_field.element([0])
            if self.y == zero:
                return ExtCurvePoint(self.curve, self.ext_field, None, None, is_infinity=True)
            # λ = (3x² + A) / (2y)
            three = self.ext_field.element([3])
            two = self.ext_field.element([2])
            numerator = three * (self.x ** 2) + A_ext
            denominator = two * self.y
            lam = numerator / denominator
        else:
            # Case 4: P + Q (general addition)
            # λ = (y_Q - y_P) / (x_Q - x_P)
            lam = (other.y - self.y) / (other.x - self.x)
        
        # Common formula: x_R = λ² - x_P - x_Q, y_R = λ(x_P - x_R) - y_P
        x_r = lam ** 2 - self.x - other.x
        y_r = lam * (self.x - x_r) - self.y
        
        return ExtCurvePoint(self.curve, self.ext_field, x_r, y_r)

    def __neg__(self) -> ExtCurvePoint:
        """Point negation: -(x, y) = (x, -y).

        Returns:
            New ExtCurvePoint representing -P.
        """
        if self.is_infinity:
            return self
        return ExtCurvePoint(self.curve, self.ext_field, self.x, -self.y)

    def __mul__(self, scalar: int) -> ExtCurvePoint:
        """Scalar multiplication using double-and-add.

        Args:
            scalar: Integer scalar.

        Returns:
            New ExtCurvePoint representing scalar * P.
        """
        # Handle special cases
        if scalar == 0:
            return ExtCurvePoint(self.curve, self.ext_field, None, None, is_infinity=True)
        if scalar < 0:
            return (-self) * (-scalar)
        
        # Double-and-add algorithm
        result = ExtCurvePoint(self.curve, self.ext_field, None, None, is_infinity=True)
        addend = self
        
        while scalar > 0:
            if scalar & 1:
                result = result + addend
            addend = addend + addend
            scalar >>= 1
        
        return result

    def __rmul__(self, scalar: int) -> ExtCurvePoint:
        """Allow scalar * point syntax."""
        return self.__mul__(scalar)

    def __eq__(self, other: object) -> bool:
        """Check point equality."""
        if not isinstance(other, ExtCurvePoint):
            return False
        if self.curve != other.curve or self.ext_field != other.ext_field:
            return False
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        if self.is_infinity:
            return "O"
        return f"({self.x}, {self.y})"


def find_point_of_order_r(
    curve: EllipticCurve,
    ext_field: ExtensionField,
    r: int,
    rng=None,
) -> ExtCurvePoint:
    """Find a point Q in E(F_{p^k}) of order r that is NOT in E(F_p).

    This point Q is the second argument to the Tate pairing. It must:
    1. Lie on the curve E(F_{p^k}).
    2. Have order r (i.e., r*Q = O).
    3. Not be in the base field E(F_p) (i.e., have a non-trivial extension component).

    Strategy:
    - Try random/systematic x-coordinates in F_{p^k} that are NOT in F_p.
    - Check if x³ + Ax + B is a square in F_{p^k}.
    - If so, compute y = sqrt(x³ + Ax + B).
    - Compute cofactor clearing: Q' = (|E(F_{p^k})| / r) * (x, y).
    - If Q' ≠ O, return Q'.

    Note: For small fields, a systematic search is fine.

    Args:
        curve: The elliptic curve.
        ext_field: The extension field F_{p^k}.
        r: The subgroup order.

    Returns:
        An ExtCurvePoint Q of order r not in E(F_p).

    Raises:
        RuntimeError: If no suitable point is found.
    """
    import random
    import math

    p = ext_field.base_field.p
    k = ext_field.k
    pk = p ** k  # |F_{p^k}|

    A_ext = ext_field.element([curve.A.value])
    B_ext = ext_field.element([curve.B.value])
    zero  = ext_field.element([0])
    one   = ext_field.element([1])
    # Euler exponent: z is a QR in F_{p^k} iff z^{(p^k-1)/2} = 1
    euler_exp = (pk - 1) // 2
    # Hasse bound: |E(F_{p^k})| lies within 2√(p^k) of p^k + 1
    hasse = int(2 * math.isqrt(pk)) + 2

    rng = rng if rng is not None else random.Random()

    for attempt in range(50_000):
        # Pick x with all k coefficients, ensuring at least one higher-degree
        # term is non-zero so x is genuinely outside F_p (and its subfields).
        # The original implementation only tried [a, b, 0, 0, ...] which
        # restricts the search to a 2-dimensional subspace of F_{p^k}.
        while True:
            coeffs = [rng.randint(0, p - 1) for _ in range(k)]
            if any(c != 0 for c in coeffs[1:]):
                break

        x = ext_field.element(coeffs)
        z = x**3 + A_ext * x + B_ext

        if z == zero:
            continue  # y = 0 gives a 2-torsion point — skip

        # Euler criterion: reject half the candidates without doing a sqrt
        if z ** euler_exp != one:
            continue

        # Compute sqrt(z) in F_{p^k}
        y = _sqrt_in_ext(z, ext_field, pk, one, rng)
        if y is None:
            continue

        point = ExtCurvePoint(curve, ext_field, x, y)

        # Cofactor clearing: we don't know |E(F_{p^k})| exactly, so we scan
        # every multiple of r inside the Hasse band [p^k+1 ± 2√(p^k)].
        # Multiplying by |E|/r maps any point into the r-torsion subgroup.
        for n_candidate in range(pk + 1 - hasse, pk + 1 + hasse + 1):
            if n_candidate % r != 0:
                continue
            Q = (n_candidate // r) * point
            if Q.is_infinity or not (r * Q).is_infinity:
                continue
            # A Q whose coordinates are constant polynomials (all higher-degree
            # coefficients zero) is actually in E(F_p), not E(F_{p^k}).
            # Such a Q gives a trivial pairing — reject it.
            if _is_in_base_field(Q):
                continue
            return Q

    raise RuntimeError(f"Could not find point of order {r} in E(F_{{{p}^{k}}})")


def _sqrt_in_ext(z, ext_field, pk: int, one, rng):
    """Return y with y² = z in ext_field, or None if not found.

    Three strategies, in order of preference:
    1. p^k ≡ 3 (mod 4): closed-form y = z^{(p^k+1)/4}  (same trick as F_p)
    2. p^k ≤ 100 000: brute-force over all elements of F_{p^k}
    3. General: Tonelli-Shanks algorithm lifted to F_{p^k}
    """
    p = ext_field.base_field.p
    k = ext_field.k

    # Strategy 1: simple formula when p^k ≡ 3 (mod 4)
    if pk % 4 == 3:
        y = z ** ((pk + 1) // 4)
        return y if y * y == z else None

    # Strategy 2: brute force for small fields (p^k ≤ 100 000)
    # For p=7, k=4: p^k = 2401 — only 2401 candidates, very fast
    if pk <= 100_000:
        from itertools import product
        for coeffs in product(range(p), repeat=k):
            y = ext_field.element(list(coeffs))
            if y * y == z:
                return y
        return None

    # Strategy 3: Tonelli-Shanks in F_{p^k}
    # Write p^k - 1 = Q * 2^S (Q odd)
    Q_ts, S = pk - 1, 0
    while Q_ts % 2 == 0:
        Q_ts //= 2
        S += 1

    # Find a quadratic non-residue w in F_{p^k}
    euler = (pk - 1) // 2
    w = None
    for _ in range(10_000):
        coeffs = [rng.randint(0, p - 1) for _ in range(k)]
        if all(c == 0 for c in coeffs):
            continue
        candidate = ext_field.element(coeffs)
        if candidate ** euler != one:
            w = candidate
            break
    if w is None:
        return None

    # Standard Tonelli-Shanks iterations
    M = S
    c = w ** Q_ts       # non-residue raised to Q
    t = z ** Q_ts       # z raised to Q
    R = z ** ((Q_ts + 1) // 2)  # candidate sqrt

    for _ in range(10_000):
        if t == one:
            return R if R * R == z else None
        # Find least i > 0 such that t^{2^i} = 1
        temp, i = t * t, 1
        while temp != one and i < M:
            temp = temp * temp
            i += 1
        if i == M:
            return None  # z is not a QR (should not happen after Euler check)
        # Update using b = c^{2^{M-i-1}}
        b = c
        for _ in range(M - i - 1):
            b = b * b
        M, c, t, R = i, b * b, t * c, R * b

    return None


def _is_in_base_field(Q: ExtCurvePoint) -> bool:
    """Return True if Q's coordinates are all in F_p (constant polynomials).

    A point with coordinates in F_p is actually in E(F_p), not genuinely in
    E(F_{p^k}). Such a point gives a trivial Tate pairing and must be rejected.
    """
    if Q.is_infinity:
        return True
    def _is_constant(elem) -> bool:
        # An element of F_{p^k} is in F_p iff all coefficients beyond degree 0 are zero
        coeffs = elem.poly.coeffs
        return all(c.value == 0 for c in coeffs[1:])
    return _is_constant(Q.x) and _is_constant(Q.y)
