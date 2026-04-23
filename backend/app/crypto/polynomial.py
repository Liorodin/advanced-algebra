"""Polynomial arithmetic over F_p.

Polynomials are represented as lists of FieldElement coefficients where
the index corresponds to the degree: [a0, a1, a2] = a0 + a1*x + a2*x².

Used primarily for:
- Constructing irreducible polynomials for extension fields F_{p^k}.
- Rabin's irreducibility test.
- Arithmetic in the extension field (elements are polynomials mod f(x)).
"""

from __future__ import annotations

from app.crypto.prime_field import FieldElement
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
        self.p = list(coefficients)

        zero = self.field.element(0)
        while len(self.p) > 1 and self.p[-1] == zero:
            self.p.pop()
        
        # Ensure zero polynomial is represented as [0] not []
        if len(self.p) == 0:
            self.p = [zero]

    @property
    def coeffs(self) -> list[FieldElement]:
        return self.p

    def degree(self) -> int:
        """Return the degree of this polynomial.

        The zero polynomial has degree -1 by convention.

        Returns:
            Integer degree, or -1 for the zero polynomial.
        """
        if len(self.p) == 1 and self.p[0] == self.field.element(0):
            return -1
        return len(self.p) - 1

    def is_monic(self) -> bool:
        """Check if the leading coefficient is 1.

        Returns:
            True if the polynomial is monic (leading coeff = 1).
        """
        return bool(self.p) and self.p[-1] == self.field.element(1)

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
        
        # Check for zero polynomials
        zero = self.field.element(0)
        if (len(self.p) == 1 and self.p[0] == zero) or (len(other.p) == 1 and other.p[0] == zero):
            return Polynomial([], self.field)

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
            ValueError: If other is the zero polynomial.
        """
        if self.field != other.field:
            raise ValueError("Polynomials must be from the same field")

        zero_elem = self.field.element(0)
        if len(other.p) == 1 and other.p[0] == zero_elem:
            raise ValueError("Other is the zero polynomial")

        r = list[FieldElement](self.p)
        d = other.degree()
        lc_b = other.p[-1]
        zero = self.field.element(0)

        while len(r) > 0 and (len(r) - 1) >= d:
            deg_r = len(r) - 1
            lc_r = r[-1]
            t = lc_r / lc_b
            s = deg_r - d
            for j in range(len(other.p)):
                r[s + j] = r[s + j] - t * other.p[j]
            while len(r) > 0 and r[-1] == zero:
                r.pop()

        return Polynomial(r, self.field)

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

        zero_elem = self.field.element(0)
        if len(other.p) == 1 and other.p[0] == zero_elem:
            raise ValueError("Other is the zero polynomial")

        dividend = list[FieldElement](self.p)
        divisor = other.p
        lc_divisor = divisor[-1]

        if len(dividend) < len(divisor):
            return Polynomial([self.field.element(0)], self.field)

        quotient = [self.field.element(0)] * (len(dividend) - len(divisor) + 1)
        zero = self.field.element(0)

        while len(dividend) >= len(divisor) and any(c != zero for c in dividend):
            deg_diff = len(dividend) - len(divisor)
            lc_dividend = dividend[-1]
            coeff = lc_dividend / lc_divisor
            quotient[deg_diff] = coeff

            for j in range(len(divisor)):
                idx = deg_diff + j
                dividend[idx] = dividend[idx] - coeff * divisor[j]

            while dividend and dividend[-1] == zero:
                dividend.pop()

        return Polynomial(quotient, self.field)

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

        Raises:
            ValueError: If exp is negative.
        """
        if exp < 0:
            raise ValueError("polynomial exponent must be non-negative")
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
        zero = self.field.element(0)
        if len(self.p) == 1 and self.p[0] == zero:
            return '0'

        terms = []
        one = self.field.element(1)

        for i, coef in enumerate[FieldElement](self.p):
            if coef == self.field.element(0):
                continue

            if i == 0:
                terms.append(str(coef))
            elif i == 1:
                terms.append(f"{'' if coef == one else coef}x")
            else:
                terms.append(f"{'' if coef == one else coef}x^{i}")

        return " + ".join(terms)

    def make_monic(self) -> Polynomial:
        zero = self.field.element(0)
        if self.is_monic() or (len(self.p) == 1 and self.p[0] == zero):
            return self
        return self / Polynomial([self.field.element(self.p[-1])], self.field)

    def gcd(self, other: Polynomial) -> Polynomial:
        """Compute GCD of two polynomials using Euclidean algorithm.

        The result is made monic (leading coefficient = 1).

        Args:
            other: Another Polynomial over the same field.

        Returns:
            The monic GCD polynomial. For gcd(0, 0), returns the zero polynomial.

        """
        if self.field != other.field:
            raise ValueError("Polynomials must be from the same field")

        zero = self.field.element(0)
        f, g = self, other
        while not (len(g.p) == 1 and g.p[0] == zero):
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
        if k != self.degree():
            raise ValueError("k must equal self.degree()")
        if k < 1:
            return False
        
        zero = self.field.element(0)
        if len(self.p) == 1 and self.p[0] == zero:
            return False

        p_char = self.field.p
        x = Polynomial([self.field.element(0), self.field.element(1)], self.field)
        one = Polynomial([self.field.element(1)], self.field)

        def distinct_prime_factors(n: int) -> list[int]:
            factors: list[int] = []
            m = n
            d = 2
            while d * d <= m:
                if m % d == 0:
                    factors.append(d)
                    while m % d == 0:
                        m //= d
                d += 1
            if m > 1:
                factors.append(m)
            return factors

        for pi in distinct_prime_factors(k):
            n_i = k // pi
            x_pow = pow(x, pow(p_char, n_i), self)
            h_i = (x_pow - x) % self
            if self.gcd(h_i) != one:
                return False

        x_pk = pow(x, pow(p_char, k), self)
        x_pk_minus_x = (x_pk - x) % self
        zero = self.field.element(0)
        return len(x_pk_minus_x.p) == 1 and x_pk_minus_x.p[0] == zero

    def extended_gcd(self, other: Polynomial) -> tuple[Polynomial, Polynomial, Polynomial]:
        """Extended Euclidean algorithm for polynomials.

        Finds polynomials g, s, t such that:
            s * self + t * other = g = gcd(self, other)

        Used for computing inverses in extension fields.

        Args:
            other: Another Polynomial over the same field.

        Returns:
            Tuple (g, s, t) where g is the GCD and s, t are Bézout coefficients.
        """
        if self.field != other.field:
            raise ValueError("Polynomials must be from the same field")

        zero = Polynomial([], self.field)
        one = Polynomial([self.field.element(1)], self.field)

        old_r, r = self, other
        old_s, s = one, zero
        old_t, t = zero, one

        zero_elem = self.field.element(0)
        while not (len(r.p) == 1 and r.p[0] == zero_elem):
            quotient = old_r / r
            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s
            old_t, t = t, old_t - quotient * t

        return old_r, old_s, old_t
