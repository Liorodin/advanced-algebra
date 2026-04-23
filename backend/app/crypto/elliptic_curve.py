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
        self.field = field
        self.A = field.element(A)
        self.B = field.element(B)
        
        # Check non-singularity: 4A³ + 27B² ≠ 0
        discriminant = field.element(4) * (self.A ** 3) + field.element(27) * (self.B ** 2)
        if discriminant.value == 0:
            raise ValueError("Curve is singular (discriminant is zero)")

    def is_non_singular(self) -> bool:
        """Check that 4A³ + 27B² ≠ 0 in F_p.

        Returns:
            True if the curve is non-singular.
        """
        discriminant = self.field.element(4) * (self.A ** 3) + self.field.element(27) * (self.B ** 2)
        return discriminant.value != 0

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
        count = 1  # Start with point at infinity
        p = self.field.p
        
        for x_val in range(p):
            x = self.field.element(x_val)
            # Compute z = x³ + Ax + B
            z = x**3 + self.A * x + self.B
            
            if z.value == 0:
                count += 1  # Only one point: (x, 0)
            elif z.is_quadratic_residue():
                count += 2  # Two points: (x, y) and (x, -y)
        
        return count

    def contains(self, point: ECPoint) -> bool:
        """Check if a point lies on this curve.

        For a non-infinity point (x, y), verify y² = x³ + Ax + B.

        Args:
            point: An ECPoint to check.

        Returns:
            True if the point is on this curve.
        """
        if point.is_infinity:
            return True
        # Check: y² = x³ + Ax + B
        lhs = point.y * point.y
        rhs = point.x**3 + self.A * point.x + self.B
        return lhs == rhs

    def identity(self) -> ECPoint:
        """Return the point at infinity (identity element of the group).

        Returns:
            ECPoint representing the point at infinity.
        """
        return ECPoint(self, None, None, is_infinity=True)

    def __repr__(self) -> str:
        return f"E: y² = x³ + {self.A}x + {self.B} over {self.field}"


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
        self.curve = curve
        self.x = x
        self.y = y
        self.is_infinity = is_infinity

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
        if self.curve != other.curve:
            raise ValueError("Points must be on the same curve")
        
        # Case 1: P + O = P
        if self.is_infinity:
            return other
        if other.is_infinity:
            return self
        
        # Case 2: P + (-P) = O (same x, opposite y)
        if self.x == other.x and self.y != other.y:
            return self.curve.identity()
        
        # Case 3: P + P (doubling)
        if self == other:
            if self.y.value == 0:
                return self.curve.identity()
            # λ = (3x² + A) / (2y)
            numerator = self.curve.field.element(3) * (self.x ** 2) + self.curve.A
            denominator = self.curve.field.element(2) * self.y
            lam = numerator / denominator
        else:
            # Case 4: P + Q (general addition)
            # λ = (y_Q - y_P) / (x_Q - x_P)
            lam = (other.y - self.y) / (other.x - self.x)
        
        # Common formula: x_R = λ² - x_P - x_Q, y_R = λ(x_P - x_R) - y_P
        x_r = lam ** 2 - self.x - other.x
        y_r = lam * (self.x - x_r) - self.y
        
        return ECPoint(self.curve, x_r, y_r)

    def __neg__(self) -> ECPoint:
        """Point negation: -(x, y) = (x, -y).

        Returns:
            New ECPoint representing -P.
        """
        if self.is_infinity:
            return self
        return ECPoint(self.curve, self.x, -self.y)

    def __mul__(self, scalar: int) -> ECPoint:
        """Scalar multiplication using double-and-add.

        Computes scalar * P efficiently using binary expansion of scalar.
        Must handle scalar = 0 (returns identity) and negative scalars.

        Args:
            scalar: Integer scalar.

        Returns:
            New ECPoint representing scalar * P.
        """
        # Handle special cases
        if scalar == 0:
            return self.curve.identity()
        if scalar < 0:
            return (-self) * (-scalar)
        
        # Double-and-add algorithm
        result = self.curve.identity()
        addend = self
        
        while scalar > 0:
            if scalar & 1:
                result = result + addend
            addend = addend + addend
            scalar >>= 1
        
        return result

    def __rmul__(self, scalar: int) -> ECPoint:
        """Allow scalar * point syntax (e.g., 7 * P).

        Args:
            scalar: Integer scalar.

        Returns:
            New ECPoint representing scalar * P.
        """
        return self.__mul__(scalar)

    def __eq__(self, other: object) -> bool:
        """Check point equality.

        Two points are equal if they're both infinity, or have the same
        coordinates on the same curve.
        """
        if not isinstance(other, ECPoint):
            return False
        if self.curve != other.curve:
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

    def order(self) -> int:
        """Compute the order of this point in the curve group.

        The order of P is the smallest positive integer n such that nP = O.
        Strategy: compute |G| = |E(F_p)|, then test divisors of |G|.

        Returns:
            The order of this point.
        """
        if self.is_infinity:
            return 1
        
        group_order = self.curve.group_order()
        
        # Test divisors of group_order
        from app.crypto.utils import prime_factors
        factors = list(set(prime_factors(group_order)))
        
        # Start with group_order and divide by prime factors
        candidates = [group_order]
        for p in factors:
            new_candidates = []
            for n in candidates:
                if n % p == 0:
                    new_candidates.append(n // p)
            candidates.extend(new_candidates)
        
        # Sort and test
        candidates = sorted(set(candidates))
        for n in candidates:
            if (n * self).is_infinity:
                return n
        
        return group_order
