"""Prime field F_p arithmetic.

This module implements the finite field Z/pZ (integers modulo a prime p).
It uses the factory pattern: create a PrimeField, then use field.element(v)
to produce FieldElement instances bound to that field.

All arithmetic operations return new FieldElement instances (immutability).
"""

from __future__ import annotations
from app.crypto.utils import is_prime, extended_gcd


class PrimeField:
    """Represents the finite field F_p = Z/pZ.

    Attributes:
        p: The prime modulus.
    """

    def __init__(self, p: int) -> None:
        """Initialize the prime field F_p.

        Must validate:
        1. p is prime (using is_prime from utils).
        2. p ≡ 3 (mod 4) — required for efficient square root computation.

        Args:
            p: The prime modulus for the field.

        Raises:
            ValueError: If p is not prime or p ≢ 3 (mod 4).
        """
        if not is_prime(p):
            raise ValueError("p must be prime")
        if p % 4 != 3:
            raise ValueError("p must satisfy p ≡ 3 (mod 4)")
        self.p = p

    def element(self, value: int) -> FieldElement:
        """Create a FieldElement in this field.

        Factory method that creates an element bound to this field.
        The value is automatically reduced mod p.

        Args:
            value: Integer value for the element.

        Returns:
            A FieldElement representing value mod p in this field.

        Examples:
            >>> F = PrimeField(103)
            >>> a = F.element(5)
            >>> b = F.element(110)  # same as F.element(7) since 110 mod 103 = 7
        """
        return FieldElement(value % self.p, self)

    def order(self) -> int:
        """Return the order (size) of the field.

        Returns:
            The prime p (the field has p elements).
        """
        return self.p

    def __repr__(self) -> str:
        return f"F_{self.p}"


class FieldElement:
    """An element of F_p.

    Supports arithmetic operations (+, -, *, /, **) all performed mod p.
    Elements are immutable — operations return new FieldElement instances.

    Attributes:
        value: The integer value in [0, p-1].
        field: The PrimeField this element belongs to.
    """

    def __init__(self, value: int, field: PrimeField) -> None:
        """Initialize a field element.

        Store value mod p to ensure it's in the canonical range [0, p-1].

        Args:
            value: Integer value (will be reduced mod p).
            field: The PrimeField this element belongs to.
        """
        self.value = value % field.p
        self.field = field

    def __add__(self, other: FieldElement) -> FieldElement:
        """Add two field elements: (a + b) mod p.

        Args:
            other: Another FieldElement in the same field.

        Returns:
            New FieldElement representing the sum.

        Raises:
            ValueError: If elements are from different fields.
        """
        if self.field != other.field:
            raise ValueError("Elements must be from the same field")
        return FieldElement((self.value + other.value), self.field)

    def __sub__(self, other: FieldElement) -> FieldElement:
        """Subtract two field elements: (a - b) mod p.

        Args:
            other: Another FieldElement in the same field.

        Returns:
            New FieldElement representing the difference.
        """
        if self.field != other.field:
            raise ValueError("Elements must be from the same field")
        return FieldElement((self.value - other.value), self.field)

    def __mul__(self, other: FieldElement) -> FieldElement:
        """Multiply two field elements: (a * b) mod p.

        Args:
            other: Another FieldElement in the same field.

        Returns:
            New FieldElement representing the product.
        """
        if self.field != other.field:
            raise ValueError("Elements must be from the same field")
        return FieldElement((self.value * other.value), self.field)

    def __truediv__(self, other: FieldElement) -> FieldElement:
        """Divide two field elements: a * b^{-1} mod p.

        Args:
            other: Another FieldElement (must be non-zero).

        Returns:
            New FieldElement representing the quotient.

        Raises:
            ZeroDivisionError: If other is zero.
        """
        if self.field != other.field:
            raise ValueError("Elements must be from the same field")
        return self * other.inverse()

    def __neg__(self) -> FieldElement:
        """Negate: return (-a) mod p.

        Returns:
            New FieldElement representing the additive inverse.
        """
        return FieldElement(-self.value, self.field)

    def __pow__(self, exp: int) -> FieldElement:
        """Exponentiation using square-and-multiply (binary method).

        Efficiently computes a^exp mod p. Must handle:
        - exp = 0 → returns 1
        - exp < 0 → compute inverse first, then raise to |exp|

        This is crucial for performance in pairing computations.

        Args:
            exp: Integer exponent.

        Returns:
            New FieldElement representing a^exp mod p.
        """
        if exp < 0:
            inv = self.inverse()
            return inv ** (-exp)

        result = FieldElement(1, self.field)
        base = FieldElement(self.value, self.field)

        while exp > 0:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1

        return result

    def __eq__(self, other: object) -> bool:
        """Check equality of two field elements.

        Two elements are equal if they have the same value and belong
        to the same field (same p).

        Args:
            other: Object to compare with.

        Returns:
            True if equal, False otherwise.
        """
        if not isinstance(other, FieldElement):
            return False
        return self.value == other.value and self.field == other.field

    def __hash__(self) -> int:
        """Hash based on value and field prime."""
        return hash((self.value, self.field.p))

    def __repr__(self) -> str:
        return str(self.value)

    def inverse(self) -> FieldElement:
        """Compute multiplicative inverse using extended Euclidean algorithm.

        Finds a^{-1} such that a * a^{-1} ≡ 1 (mod p).
        Uses extended_gcd from utils.

        Returns:
            New FieldElement representing a^{-1} mod p.

        Raises:
            ZeroDivisionError: If self.value is 0.
        """
        g, x, _ = extended_gcd(self.value, self.field.p)
        if g != 1:
            raise ZeroDivisionError("Element is not invertible")
        return FieldElement(x % self.field.p, self.field)

    def is_quadratic_residue(self) -> bool:
        """Test if this element is a quadratic residue mod p (Euler's criterion).

        An element a is a QR if a^{(p-1)/2} ≡ 1 (mod p).
        Zero is considered a QR.

        Returns:
            True if a is a quadratic residue mod p.

        Used by hash_to_point to check if a candidate x gives a valid curve point.
        """
        return pow(self.value, (self.field.p - 1) // 2, self.field.p) == 1

    def sqrt(self) -> FieldElement:
        """Compute square root for p ≡ 3 (mod 4).

        When p ≡ 3 (mod 4), the square root of a is simply a^{(p+1)/4} mod p.
        This is why we require p ≡ 3 (mod 4) in PrimeField.

        Returns:
            New FieldElement z such that z² ≡ self (mod p).

        Raises:
            ValueError: If self is not a quadratic residue.
        """
        if not self.is_quadratic_residue():
            raise ValueError("Element is not a quadratic residue")
        return FieldElement(pow(self.value, (self.field.p + 1) // 4, self.field.p), self.field)
