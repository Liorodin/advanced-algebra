"""Extension field F_{p^k} = F_p[x] / ⟨f(x)⟩.

Elements of the extension field are polynomials of degree < k, with
arithmetic performed modulo an irreducible polynomial f(x) of degree k.

This module also provides utilities for finding irreducible polynomials
and computing the embedding degree.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.crypto.prime_field import PrimeField, FieldElement
    from app.crypto.polynomial import Polynomial


class ExtensionField:
    """The extension field F_{p^k} = F_p[x] / ⟨f(x)⟩.

    Attributes:
        base_field: The underlying prime field F_p.
        modulus: The irreducible polynomial f(x) of degree k.
        k: The extension degree.
    """

    def __init__(self, base_field: PrimeField, irreducible_poly: Polynomial) -> None:
        """Initialize the extension field.

        Args:
            base_field: The prime field F_p.
            irreducible_poly: An irreducible polynomial of degree k over F_p.

        Raises:
            ValueError: If the polynomial is not irreducible.
        """
        from app.crypto.polynomial import Polynomial
        
        k = irreducible_poly.degree()
        if k < 1:
            raise ValueError("Irreducible polynomial must have degree >= 1")
        if not irreducible_poly.is_irreducible(k):
            raise ValueError("Polynomial is not irreducible")
        
        self.base_field = base_field
        self.modulus = irreducible_poly
        self.k = k

    def element(self, coefficients: list[int]) -> ExtFieldElement:
        """Create an element of the extension field.

        The coefficients list represents a polynomial a0 + a1*x + ... + a_{k-1}*x^{k-1}.
        Values are taken as integers and converted to FieldElements.

        Args:
            coefficients: List of integer coefficients [a0, a1, ..., a_{k-1}].
                          Padded with zeros if shorter than k.

        Returns:
            An ExtFieldElement in this extension field.
        """
        from app.crypto.polynomial import Polynomial
        
        # Convert int coefficients to FieldElements
        field_coeffs = [self.base_field.element(c) for c in coefficients]
        poly = Polynomial(field_coeffs, self.base_field)
        
        return ExtFieldElement(poly, self)

    @staticmethod
    def find_irreducible(base_field: PrimeField, k: int) -> Polynomial:
        """Find a monic irreducible polynomial of degree k over F_p.

        Strategy: iterate over monic polynomials of degree k (with constant
        term set to make it likely irreducible) and test each using Rabin's test.

        For k=2 and p ≡ 3 (mod 4), x² + 1 is always irreducible since
        -1 is not a quadratic residue.

        Args:
            base_field: The prime field F_p.
            k: The desired degree.

        Returns:
            A monic irreducible Polynomial of degree k over F_p.
        """
        from app.crypto.polynomial import Polynomial
        
        # Special case: k=2 and p ≡ 3 (mod 4) → x² + 1 is irreducible
        if k == 2 and base_field.p % 4 == 3:
            # x² + 1
            coeffs = [base_field.element(1), base_field.element(0), base_field.element(1)]
            return Polynomial(coeffs, base_field)
        
        # General case: systematic search for irreducible polynomial
        # Try polynomials of the form x^k + ... + constant
        # Start with constant term 1 (or 2 for better odds)
        from itertools import product
        
        p = base_field.p
        one = base_field.element(1)
        
        # For small k, try all combinations
        # Coefficients for x^0, x^1, ..., x^{k-1} (x^k coefficient is always 1)
        for coeff_tuple in product(range(p), repeat=k):
            coeffs = [base_field.element(c) for c in coeff_tuple]
            coeffs.append(one)  # Make it monic (leading coeff = 1)
            
            poly = Polynomial(coeffs, base_field)
            if poly.is_irreducible(k):
                return poly
        
        raise RuntimeError(f"Could not find irreducible polynomial of degree {k} over F_{p}")

    @staticmethod
    def find_embedding_degree(p: int, r: int) -> int:
        """Find the embedding degree k — smallest positive integer where r | p^k - 1.

        The embedding degree determines the extension field F_{p^k} in which
        the Tate pairing takes values. We need r to divide p^k - 1 so that
        the pairing is non-degenerate.

        Args:
            p: The field characteristic.
            r: The subgroup order.

        Returns:
            The smallest positive k such that p^k ≡ 1 (mod r).

        Example:
            For p=103, r=13: k=2 since 103² - 1 = 10608 = 13 * 816.
        """
        k = 1
        while pow(p, k, r) != 1:
            k += 1
            if k > 1000:  # Safety check
                raise RuntimeError(f"Could not find embedding degree for p={p}, r={r}")
        return k

    def __repr__(self) -> str:
        return f"F_{self.base_field.p}^{self.k}"


class ExtFieldElement:
    """An element of the extension field F_{p^k}.

    Internally represented as a Polynomial of degree < k, with arithmetic
    performed modulo the irreducible polynomial f(x).

    Attributes:
        poly: The Polynomial representing this element.
        ext_field: The ExtensionField this element belongs to.
    """

    def __init__(self, poly: Polynomial, ext_field: ExtensionField) -> None:
        """Initialize an extension field element.

        The polynomial is reduced modulo the irreducible polynomial of the field.

        Args:
            poly: A Polynomial over the base field.
            ext_field: The extension field.
        """
        self.ext_field = ext_field
        self.poly = poly % ext_field.modulus

    def __add__(self, other: ExtFieldElement) -> ExtFieldElement:
        """Add two extension field elements.

        Returns:
            New ExtFieldElement representing the sum.
        """
        if self.ext_field != other.ext_field:
            raise ValueError("Elements must be from the same extension field")
        result_poly = (self.poly + other.poly) % self.ext_field.modulus
        return ExtFieldElement(result_poly, self.ext_field)

    def __sub__(self, other: ExtFieldElement) -> ExtFieldElement:
        """Subtract two extension field elements.

        Returns:
            New ExtFieldElement representing the difference.
        """
        if self.ext_field != other.ext_field:
            raise ValueError("Elements must be from the same extension field")
        result_poly = (self.poly - other.poly) % self.ext_field.modulus
        return ExtFieldElement(result_poly, self.ext_field)

    def __mul__(self, other: ExtFieldElement) -> ExtFieldElement:
        """Multiply two extension field elements.

        Returns:
            New ExtFieldElement representing the product.
        """
        if self.ext_field != other.ext_field:
            raise ValueError("Elements must be from the same extension field")
        result_poly = (self.poly * other.poly) % self.ext_field.modulus
        return ExtFieldElement(result_poly, self.ext_field)

    def __truediv__(self, other: ExtFieldElement) -> ExtFieldElement:
        """Divide: self * other^{-1} in the extension field.

        Returns:
            New ExtFieldElement representing the quotient.

        Raises:
            ZeroDivisionError: If other is the zero element.
        """
        return self * other.inverse()

    def __pow__(self, exp: int) -> ExtFieldElement:
        """Exponentiation using square-and-multiply in the extension field.

        Args:
            exp: Integer exponent.

        Returns:
            New ExtFieldElement representing self^exp.
        """
        from app.crypto.polynomial import Polynomial
        
        if exp < 0:
            return self.inverse() ** (-exp)
        
        if exp == 0:
            one_poly = Polynomial([self.ext_field.base_field.element(1)], self.ext_field.base_field)
            return ExtFieldElement(one_poly, self.ext_field)
        
        # Square-and-multiply
        result = ExtFieldElement(
            Polynomial([self.ext_field.base_field.element(1)], self.ext_field.base_field),
            self.ext_field
        )
        base = self
        
        while exp > 0:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        
        return result

    def __neg__(self) -> ExtFieldElement:
        """Negate the element.

        Returns:
            New ExtFieldElement representing -self.
        """
        from app.crypto.polynomial import Polynomial
        neg_coeffs = [-c for c in self.poly.coeffs]
        neg_poly = Polynomial(neg_coeffs, self.ext_field.base_field)
        return ExtFieldElement(neg_poly, self.ext_field)

    def __eq__(self, other: object) -> bool:
        """Check equality of extension field elements."""
        if not isinstance(other, ExtFieldElement):
            return False
        if self.ext_field != other.ext_field:
            return False
        return self.poly == other.poly

    def __repr__(self) -> str:
        # For k=2, display as "a + bi" format
        if self.ext_field.k == 2:
            coeffs = self.poly.coeffs
            a = coeffs[0].value if len(coeffs) > 0 else 0
            b = coeffs[1].value if len(coeffs) > 1 else 0
            
            if b == 0:
                return str(a)
            elif a == 0:
                return f"{b}i" if b != 1 else "i"
            else:
                return f"{a} + {b}i"
        else:
            # Generic polynomial representation
            return str(self.poly)

    def inverse(self) -> ExtFieldElement:
        """Compute multiplicative inverse using extended GCD for polynomials.

        Find g(x) such that self * g(x) ≡ 1 (mod f(x)).
        This uses the extended Euclidean algorithm for polynomials.

        Returns:
            New ExtFieldElement representing self^{-1}.

        Raises:
            ZeroDivisionError: If self is the zero element.
        """
        zero_elem = self.ext_field.base_field.element(0)
        if len(self.poly.coeffs) == 1 and self.poly.coeffs[0] == zero_elem:
            raise ZeroDivisionError("Cannot invert zero element")
        
        g, s, t = self.poly.extended_gcd(self.ext_field.modulus)
        
        # g should be a constant polynomial (degree 0)
        if g.degree() != 0:
            raise ZeroDivisionError("Element is not invertible")
        
        # Normalize: divide s by the constant g to get the true inverse
        from app.crypto.polynomial import Polynomial
        one = self.ext_field.base_field.element(1)
        g_constant = g.coeffs[0]
        
        # s / g_constant gives us the inverse
        inv_poly = Polynomial([c / g_constant for c in s.coeffs], self.ext_field.base_field)
        
        return ExtFieldElement(inv_poly, self.ext_field)
