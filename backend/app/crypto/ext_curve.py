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
        raise NotImplementedError(
            "ExtCurvePoint.__init__: Store curve, ext_field, x, y, is_infinity"
        )

    def __add__(self, other: ExtCurvePoint) -> ExtCurvePoint:
        """Point addition on E(F_{p^k}).

        Same formulas as ECPoint.__add__, but using ExtFieldElement arithmetic.

        Args:
            other: Another ExtCurvePoint on the same curve.

        Returns:
            New ExtCurvePoint representing the sum.
        """
        raise NotImplementedError(
            "ExtCurvePoint.__add__: Same formulas as ECPoint but with extension field arithmetic"
        )

    def __neg__(self) -> ExtCurvePoint:
        """Point negation: -(x, y) = (x, -y).

        Returns:
            New ExtCurvePoint representing -P.
        """
        raise NotImplementedError("ExtCurvePoint.__neg__: Return (x, -y)")

    def __mul__(self, scalar: int) -> ExtCurvePoint:
        """Scalar multiplication using double-and-add.

        Args:
            scalar: Integer scalar.

        Returns:
            New ExtCurvePoint representing scalar * P.
        """
        raise NotImplementedError("ExtCurvePoint.__mul__: Double-and-add")

    def __rmul__(self, scalar: int) -> ExtCurvePoint:
        """Allow scalar * point syntax."""
        raise NotImplementedError("ExtCurvePoint.__rmul__: Return self * scalar")

    def __eq__(self, other: object) -> bool:
        """Check point equality."""
        raise NotImplementedError("ExtCurvePoint.__eq__: Compare coordinates")

    def __repr__(self) -> str:
        raise NotImplementedError("ExtCurvePoint.__repr__")


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
    raise NotImplementedError(
        "find_point_of_order_r: Search for Q in E(F_{p^k}) \\ E(F_p) with order r. "
        "Try extension field points, cofactor-clear, check order."
    )
