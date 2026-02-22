"""Polynomial arithmetic over F_p.

Polynomials are represented as lists of FieldElement coefficients where
the index corresponds to the degree: [a0, a1, a2] = a0 + a1*x + a2*x².

Used primarily for:
- Constructing irreducible polynomials for extension fields F_{p^k}.
- Rabin's irreducibility test.
- Arithmetic in the extension field (elements are polynomials mod f(x)).
"""

from __future__ import annotations
from itertools import zip_longest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.crypto.prime_field import PrimeField, FieldElement


class Polynomial:
    """A polynomial with coefficients in F_p.

    Coefficients are stored as a list where index i holds the coefficient
    of x^i. Trailing zero coefficients are stripped to maintain a canonical form.

    Attributes:
        coeffs: List of FieldElement coefficients [a0, a1, ..., a_n].
        field: The PrimeField the coefficients belong to.
    """

    def __init__(self, coefficients: list[FieldElement], field: PrimeField) -> None:
        """Initialize a polynomial.

        Strip trailing zero coefficients to maintain canonical form.
        An empty list or all-zero list represents the zero polynomial.

        Args:
            coefficients: List of FieldElement coefficients (index = degree).
            field: The underlying prime field F_p.

        Examples:
            >>> F = PrimeField(103)
            >>> # Represents 1 + 0*x + 1*x² = x² + 1
            >>> p = Polynomial([F.element(1), F.element(0), F.element(1)], F)
        """
        self.field = field
        self.p = coefficients
        self.null = Polynomial([], field)

        while len(self.p) > 0 and self.p[-1] == 0:
            self.p.pop()

    def degree(self) -> int:
        """Return the degree of this polynomial.

        The zero polynomial has degree -1 by convention.

        Returns:
            Integer degree, or -1 for the zero polynomial.
        """
        return len(self.p) - 1

    def is_monic(self) -> bool:
        """Check if the leading coefficient is 1.

        Returns:
            True if the polynomial is monic (leading coeff = 1).
        """
        return self.p and self.p[-1] == 1

    def __add__(self, other: Polynomial) -> Polynomial:
        """Add two polynomials coefficient-wise.

        Args:
            other: Another Polynomial over the same field.

        Returns:
            New Polynomial representing the sum.
        """
        if self.field != other.field:
            raise ValueError("Polynomials must be from the same field")

        return Polynomial([a + b for a, b in zip_longest(self.p, other.p, fillvalue = self.field.element(0))], self.field) 

    def __sub__(self, other: Polynomial) -> Polynomial:
        """Subtract two polynomials coefficient-wise.

        Args:
            other: Another Polynomial over the same field.

        Returns:
            New Polynomial representing the difference.
        """
        if self.field != other.field:
            raise ValueError("Polynomials must be from the same field")

        return Polynomial([a - b for a, b in zip_longest(self.p, other.p, fillvalue = self.field.element(0))], self.field) 

    def __mul__(self, other: Polynomial) -> Polynomial:
        """Multiply two polynomials (convolution of coefficients).

        Uses the standard O(n*m) algorithm:
        (sum a_i x^i) * (sum b_j x^j) = sum_{k} (sum_{i+j=k} a_i * b_j) x^k

        Args:
            other: Another Polynomial over the same field.

        Returns:
            New Polynomial representing the product.
        """
        if self.field != other.field:
            raise ValueError("Polynomials must be from the same field")
        
        if not self.p or not other.p:
            return self.null

        result_len = self.degree() + other.degree() + 1
        result = [self.field.element(0)] * result_len
        
        for i, a in enumerate(self.p):
            for j, b in enumerate(other.p):
                result[i + j] += a * b

        return Polynomial(result, self.field)

    def __mod__(self, other: Polynomial) -> Polynomial:
        """Compute remainder of polynomial division (self mod other).

        Uses the standard polynomial long division algorithm.
        This is the core operation for extension field arithmetic:
        elements of F_{p^k} are polynomials mod f(x).

        Args:
            other: The divisor polynomial (must be non-zero).

        Returns:
            The remainder polynomial.

        Raises:
            ZeroDivisionError: If other is the zero polynomial.
        """  
        if self.field != other.field:
            raise ValueError("Polynomials must be from the same field")

        if not other.p:
            raise ValueError("Other is the zero polynomial")

    def __truediv__(self, other: Polynomial) -> Polynomial:
        """Compute quotient of polynomial division.

        Args:
            other: The divisor polynomial (must be non-zero).

        Returns:
            The quotient polynomial.

        Raises:
            ZeroDivisionError: If other is the zero polynomial.
        """
        if self.field != other.field:
            raise ValueError("Polynomials must be from the same field")

        if not other.p:
            raise ValueError("Other is the zero polynomial")

        raise NotImplementedError(
            "Polynomial.is_irreducible: Implement Rabin's irreducibility test"
        )

    def __pow__(self, exp: int, modulus: Polynomial | None = None) -> Polynomial:
        """Exponentiation with optional polynomial modulus.

        Computes self^exp mod modulus using square-and-multiply.
        When modulus is provided, reduce mod modulus after each multiplication
        to keep intermediate results small.

        This is used in Rabin's irreducibility test: x^{p^n} mod f(x).

        Args:
            exp: Non-negative integer exponent.
            modulus: Optional polynomial to reduce modulo after each step.

        Returns:
            Resulting polynomial (reduced mod modulus if given).
        """
        result = Polynomial([self.field.element(1)], self.field)
        base = self

        while exp > 0:
            if exp % 2 == 1:
                result = result * base
                if modulus:
                    result = result % modulus
            base = base * base
            if modulus:
                base = base % modulus
            exp //= 2

        return result

    def __eq__(self, other: object) -> bool:
        """Check polynomial equality (same coefficients)."""
        if not isinstance(other, Polynomial):
            return False
        return self.field == other.field and self.p == other.p

    def __repr__(self) -> str:
        if not self.p:
            return '0'

        terms = []

        for i, coef in enumerate(self.p):
            if coef == 0:
                continue

            if i == 0:
                terms.append(str(coef))
            elif i == 1:
                terms.append(f"{'' if coef == 1 else coef}x")
            else:
                terms.append(f"{'' if coef == 1 else coef}x^{i}")

        return " + ".join(terms)

    def make_monic(self) -> Polynomial:
        if self.is_monic() or not self.p:
            return self
        return self / Polynomial([self.field.element(self.p[-1])], self.field)

    def gcd(self, other: Polynomial) -> Polynomial:
        """Compute GCD of two polynomials using Euclidean algorithm.

        The result is made monic (leading coefficient = 1).

        Args:
            other: Another Polynomial over the same field.

        Returns:
            The monic GCD polynomial.
        """
        if self.field != other.field:
            raise ValueError("Polynomials must be from the same field")

        f, g = self, other
        while g.p:
            r = f % g
            f, g = g, r
        return f.make_monic()

    def is_irreducible(self, k: int) -> bool:
        """Test if this polynomial is irreducible over F_p using Rabin's test.

        Rabin's irreducibility test for f(x) of degree k:
        1. Let p1, p2, ..., pt be the distinct prime divisors of k.
        2. For each i, compute n_i = k / p_i.
        3. For each i, compute h_i(x) = x^{p^{n_i}} - x  mod f(x).
        4. Check that gcd(h_i(x), f(x)) = 1 for all i.
        5. Check that x^{p^k} ≡ x (mod f(x)).

        If all checks pass, f(x) is irreducible over F_p.

        Args:
            k: The degree of this polynomial (must equal self.degree()).

        Returns:
            True if the polynomial is irreducible over F_p.
        """
        raise NotImplementedError(
            "Polynomial.is_irreducible: Implement Rabin's irreducibility test"
        )
