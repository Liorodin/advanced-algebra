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
    p = ext_field.base_field.p
    k = ext_field.k
    
    # Embed curve coefficients into extension field
    A_ext = ext_field.element([curve.A.value])
    B_ext = ext_field.element([curve.B.value])
    
    # For k=2, try points with non-zero imaginary component
    # Try x = a + bi where b != 0
    for a in range(p):
        for b in range(1, p):  # b must be non-zero (not in base field)
            x = ext_field.element([a, b])
            
            # Compute z = x³ + Ax + B
            z = x**3 + A_ext * x + B_ext
            
            # Try to find y such that y² = z
            # For small fields, brute force search
            for c in range(p):
                for d in range(p):
                    y = ext_field.element([c, d])
                    if y * y == z:
                        # Found a point on the curve
                        point = ExtCurvePoint(curve, ext_field, x, y)
                        
                        # Apply cofactor clearing
                        # Need to compute |E(F_{p^k})| - approximately p^k + 1
                        # For more accurate count, use the fact that for small fields
                        # we can estimate or compute exactly
                        # For now, use a heuristic: cofactor ≈ (p^k + 1) / r
                        pk = p ** k
                        # Hasse bound: |E(F_{p^k})| is in [p^k + 1 - 2√(p^k), p^k + 1 + 2√(p^k)]
                        # Try a few candidates around p^k + 1
                        for group_order_candidate in range(pk + 1 - int(2 * (pk ** 0.5)), 
                                                          pk + 1 + int(2 * (pk ** 0.5)) + 1):
                            if group_order_candidate % r == 0:
                                cofactor = group_order_candidate // r
                                Q = cofactor * point
                                
                                # Check if Q has order r and is not infinity
                                if not Q.is_infinity:
                                    # Verify order r
                                    if (r * Q).is_infinity:
                                        return Q
            
    raise RuntimeError(f"Could not find point of order {r} in E(F_{{{p}^{k}}})")
