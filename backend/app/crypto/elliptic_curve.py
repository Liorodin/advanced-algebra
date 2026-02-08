"""Elliptic curve E(F_p): y² = x³ + Ax + B over a prime field.

Implements the elliptic curve group law (point addition, doubling,
scalar multiplication) for points with coordinates in F_p.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.crypto.prime_field import PrimeField, FieldElement


class EllipticCurve:
    """An elliptic curve y² = x³ + Ax + B over F_p.

    Attributes:
        field: The PrimeField F_p.
        A: Coefficient A as a FieldElement.
        B: Coefficient B as a FieldElement.
    """

    def __init__(self, field: PrimeField, A: int, B: int) -> None:
        """Initialize the elliptic curve with parameters.

        Must validate that the curve is non-singular:
        4A³ + 27B² ≠ 0 (mod p).

        Args:
            field: The prime field F_p.
            A: Integer coefficient A (will be converted to FieldElement).
            B: Integer coefficient B (will be converted to FieldElement).

        Raises:
            ValueError: If the discriminant is zero (singular curve).
        """
        raise NotImplementedError(
            "EllipticCurve.__init__: Store field, A, B as FieldElements. "
            "Check 4A³ + 27B² ≠ 0"
        )

    def is_non_singular(self) -> bool:
        """Check that 4A³ + 27B² ≠ 0 in F_p.

        Returns:
            True if the curve is non-singular.
        """
        raise NotImplementedError(
            "EllipticCurve.is_non_singular: Compute discriminant in the field"
        )

    def group_order(self) -> int:
        """Compute |E(F_p)| — the number of points on the curve including infinity.

        Approach: Naive point counting — iterate over all x in F_p, check if
        x³ + Ax + B is a quadratic residue. If yes, that x gives 2 points
        (for ±y). Don't forget the point at infinity.

        For small primes (like p = 103), naive counting is perfectly fine.
        For larger primes, consider baby-step giant-step or Schoof's algorithm.

        Returns:
            Integer count of points on E(F_p).

        Example:
            For p=103, A=1, B=0: |E(F_103)| = 104
        """
        raise NotImplementedError(
            "EllipticCurve.group_order: Count points by iterating x in F_p. "
            "For each x, check if x³+Ax+B is a QR → 2 points; if zero → 1 point. "
            "Add 1 for point at infinity."
        )

    def contains(self, point: ECPoint) -> bool:
        """Check if a point lies on this curve.

        For a non-infinity point (x, y), verify y² = x³ + Ax + B.

        Args:
            point: An ECPoint to check.

        Returns:
            True if the point is on this curve.
        """
        raise NotImplementedError(
            "EllipticCurve.contains: Check y² == x³ + Ax + B (or point is infinity)"
        )

    def identity(self) -> ECPoint:
        """Return the point at infinity (identity element of the group).

        Returns:
            ECPoint representing the point at infinity.
        """
        raise NotImplementedError(
            "EllipticCurve.identity: Return ECPoint with is_infinity=True"
        )

    def __repr__(self) -> str:
        raise NotImplementedError("EllipticCurve.__repr__")


class ECPoint:
    """A point on an elliptic curve E(F_p).

    Points are immutable — all operations return new ECPoint instances.

    Attributes:
        curve: The EllipticCurve this point belongs to.
        x: The x-coordinate (FieldElement), or None if infinity.
        y: The y-coordinate (FieldElement), or None if infinity.
        is_infinity: True if this is the point at infinity.
    """

    def __init__(
        self,
        curve: EllipticCurve,
        x: FieldElement | None,
        y: FieldElement | None,
        is_infinity: bool = False,
    ) -> None:
        """Initialize a point on the curve.

        Args:
            curve: The elliptic curve.
            x: x-coordinate (FieldElement) or None for infinity.
            y: y-coordinate (FieldElement) or None for infinity.
            is_infinity: Whether this is the point at infinity.
        """
        raise NotImplementedError(
            "ECPoint.__init__: Store curve, x, y, is_infinity"
        )

    def __add__(self, other: ECPoint) -> ECPoint:
        """Elliptic curve point addition.

        Implements the full group law:
        1. P + O = P, O + P = P (identity cases)
        2. P + (-P) = O (inverse case: same x, opposite y)
        3. P + P (doubling): λ = (3x² + A) / (2y), then x_R = λ² - 2x, y_R = λ(x - x_R) - y
        4. P + Q (general): λ = (y_Q - y_P) / (x_Q - x_P), then x_R = λ² - x_P - x_Q, y_R = λ(x_P - x_R) - y_P

        Args:
            other: Another ECPoint on the same curve.

        Returns:
            New ECPoint representing the sum P + Q.
        """
        raise NotImplementedError(
            "ECPoint.__add__: Implement point addition with all cases"
        )

    def __neg__(self) -> ECPoint:
        """Point negation: -(x, y) = (x, -y).

        Returns:
            New ECPoint representing -P.
        """
        raise NotImplementedError("ECPoint.__neg__: Return (x, -y) or O if infinity")

    def __mul__(self, scalar: int) -> ECPoint:
        """Scalar multiplication using double-and-add.

        Computes scalar * P efficiently using binary expansion of scalar.
        Must handle scalar = 0 (returns identity) and negative scalars.

        Args:
            scalar: Integer scalar.

        Returns:
            New ECPoint representing scalar * P.
        """
        raise NotImplementedError(
            "ECPoint.__mul__: Double-and-add algorithm for scalar * P"
        )

    def __rmul__(self, scalar: int) -> ECPoint:
        """Allow scalar * point syntax (e.g., 7 * P).

        Args:
            scalar: Integer scalar.

        Returns:
            New ECPoint representing scalar * P.
        """
        raise NotImplementedError("ECPoint.__rmul__: Return self.__mul__(scalar)")

    def __eq__(self, other: object) -> bool:
        """Check point equality.

        Two points are equal if they're both infinity, or have the same
        coordinates on the same curve.
        """
        raise NotImplementedError("ECPoint.__eq__: Compare coordinates and curve")

    def __repr__(self) -> str:
        raise NotImplementedError("ECPoint.__repr__: Return '(x, y)' or 'O' for infinity")

    def order(self) -> int:
        """Compute the order of this point in the curve group.

        The order of P is the smallest positive integer n such that nP = O.
        Strategy: compute |G| = |E(F_p)|, then test divisors of |G|.

        Returns:
            The order of this point.
        """
        raise NotImplementedError(
            "ECPoint.order: Compute |G|, then find smallest divisor d of |G| where d*self = O"
        )
