"""Unit tests for app.crypto.polynomial — TDD style."""

import pytest
from app.crypto.prime_field import PrimeField
from app.crypto.polynomial import Polynomial


@pytest.fixture
def field():
    return PrimeField(103)


@pytest.fixture
def poly_x2_plus_1(field):
    # x^2 + 1
    return Polynomial([field.element(1), field.element(0), field.element(1)], field)


@pytest.fixture
def poly_x(field):
    return Polynomial([field.element(0), field.element(1)], field)


class TestPolynomialInit:
    def test_init_strips_trailing_zeros(self, field):
        p = Polynomial([field.element(1), field.element(0), field.element(0)], field)
        assert p.degree() == 0

    def test_init_zero_polynomial(self, field):
        p = Polynomial([], field)
        assert p.degree() == -1

    def test_degree(self, poly_x2_plus_1):
        assert poly_x2_plus_1.degree() == 2

    def test_is_monic(self, poly_x2_plus_1, field):
        assert poly_x2_plus_1.is_monic() is True
        not_monic = Polynomial([field.element(1), field.element(2)], field)
        assert not_monic.is_monic() is True  # leading 2, so not monic if degree 1
        two_x = Polynomial([field.element(0), field.element(2)], field)
        assert two_x.is_monic() is False


class TestPolynomialArithmetic:
    def test_add(self, field):
        p = Polynomial([field.element(1), field.element(1)], field)
        q = Polynomial([field.element(1), field.element(0)], field)
        r = p + q
        assert r.degree() >= 0
        # 1+x + 1 = 2+x
        assert r.coeffs[0].value == 2 and r.coeffs[1].value == 1

    def test_sub(self, field):
        p = Polynomial([field.element(3), field.element(1)], field)
        q = Polynomial([field.element(1), field.element(0)], field)
        r = p - q
        assert (r.coeffs[0].value, r.coeffs[1].value) == (2, 1)

    def test_mul(self, field):
        # (x+1)*(x+1) = x^2+2x+1
        p = Polynomial([field.element(1), field.element(1)], field)
        r = p * p
        assert r.degree() == 2
        assert r.coeffs[0].value == 1 and r.coeffs[1].value == 2 and r.coeffs[2].value == 1

    def test_mod(self, field):
        # x^2 + 1 mod x = 1
        high = Polynomial([field.element(1), field.element(0), field.element(1)], field)
        divisor = Polynomial([field.element(0), field.element(1)], field)
        rem = high % divisor
        assert rem.degree() == 0
        assert rem.coeffs[0].value == 1

    def test_div_quotient(self, field):
        # x^2 + 1 = (x)(x) + 1, so quotient of (x^2+1) / x is x
        high = Polynomial([field.element(1), field.element(0), field.element(1)], field)
        divisor = Polynomial([field.element(0), field.element(1)], field)
        quot = high / divisor
        assert quot.degree() == 1
        assert quot.coeffs[1].value == 1

    def test_pow_with_modulus(self, field, poly_x2_plus_1):
        # x^2 mod (x^2+1) for p=103: x^2 ≡ -1
        poly_x = Polynomial([field.element(0), field.element(1)], field)
        result = poly_x ** 2 % poly_x2_plus_1
        # result should be -1 = 102 mod 103
        assert result.degree() == 0
        assert result.coeffs[0].value == 102

    def test_gcd(self, field):
        # gcd(x^2-1, x-1) = x-1 (up to scalar)
        # Over F_p: x^2-1 = (x-1)(x+1)
        one = field.element(1)
        zero = field.element(0)
        m1 = field.element(-1)
        p = Polynomial([m1, zero, one], field)   # x^2 - 1
        q = Polynomial([m1, one], field)          # x - 1
        g = p.gcd(q)
        assert g.is_monic()
        assert g.degree() == 1

    def test_eq(self, field):
        p = Polynomial([field.element(1), field.element(0)], field)
        q = Polynomial([field.element(1), field.element(0)], field)
        assert p == q

    def test_is_irreducible_x2_plus_1(self, field):
        # x^2 + 1 over F_p with p ≡ 3 mod 4: -1 is not QR, so x^2+1 is irreducible
        irr = Polynomial([field.element(1), field.element(0), field.element(1)], field)
        assert irr.is_irreducible(2) is True

    def test_repr(self, poly_x2_plus_1):
        r = repr(poly_x2_plus_1)
        assert r is not None
        assert len(r) > 0
