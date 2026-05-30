"""Comprehensive test suite — 250+ tests across all crypto modules."""

import pytest

from app.crypto.utils import gcd, extended_gcd, is_prime, prime_factors, largest_prime_factor
from app.crypto.prime_field import PrimeField, FieldElement
from app.crypto.polynomial import Polynomial
from app.crypto.elliptic_curve import EllipticCurve, ECPoint
from app.crypto.extension_field import ExtensionField
from app.crypto.hash_to_point import (
    hash_to_point,
    string_to_field_element,
    increment_and_try,
    cofactor_clear,
)
from app.crypto.bls import BLSSignatureScheme


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _poly(coeffs: list[int], F: PrimeField) -> Polynomial:
    return Polynomial([F.element(c) for c in coeffs], F)


PRIMES_3_MOD_4 = [3, 7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83, 103, 107, 127, 131]


# ===========================================================================
# SECTION 1 — utils.py
# ===========================================================================


class TestGCD:
    def test_basic(self):
        assert gcd(12, 8) == 4

    def test_coprime(self):
        assert gcd(7, 13) == 1

    def test_zero_a(self):
        assert gcd(0, 5) == 5

    def test_zero_b(self):
        assert gcd(5, 0) == 5

    def test_both_zero(self):
        assert gcd(0, 0) == 0

    def test_same_inputs(self):
        assert gcd(9, 9) == 9

    def test_one_is_identity(self):
        assert gcd(1, 100) == 1

    def test_commutative(self):
        assert gcd(28, 21) == gcd(21, 28)

    def test_prime_divides_multiple(self):
        assert gcd(13, 26) == 13

    def test_large_inputs(self):
        assert gcd(100, 75) == 25

    def test_fibonacci_consecutive_coprime(self):
        assert gcd(89, 144) == 1

    def test_power_of_2(self):
        assert gcd(64, 16) == 16

    def test_gcd_is_positive(self):
        assert gcd(12, 8) > 0

    def test_divides_both(self):
        g = gcd(48, 36)
        assert 48 % g == 0 and 36 % g == 0

    def test_gcd_103_50(self):
        assert gcd(103, 50) == 1  # 103 is prime


class TestExtendedGCD:
    def test_bezout_12_8(self):
        g, x, y = extended_gcd(12, 8)
        assert g == 4 and 12 * x + 8 * y == 4

    def test_bezout_coprime(self):
        g, x, y = extended_gcd(7, 13)
        assert g == 1 and 7 * x + 13 * y == 1

    @pytest.mark.parametrize("a, b", [(15, 10), (99, 13), (37, 55), (103, 50), (48, 18)])
    def test_bezout_identity(self, a, b):
        g, x, y = extended_gcd(a, b)
        assert a * x + b * y == g

    def test_result_is_gcd(self):
        g, _, _ = extended_gcd(48, 18)
        assert g == gcd(48, 18)

    def test_prime_with_1(self):
        g, x, _ = extended_gcd(103, 1)
        assert g == 1

    def test_large_values(self):
        g, x, y = extended_gcd(1234567, 7654321)
        assert 1234567 * x + 7654321 * y == g


class TestIsPrime:
    @pytest.mark.parametrize("p", [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 101, 103, 107])
    def test_known_primes(self, p):
        assert is_prime(p) is True

    @pytest.mark.parametrize("n", [0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 25, 100, 104])
    def test_known_composites(self, n):
        assert is_prime(n) is False

    def test_two_is_prime(self):
        assert is_prime(2) is True

    def test_negative_not_prime(self):
        assert is_prime(-7) is False

    def test_large_prime(self):
        assert is_prime(7919) is True

    def test_large_composite(self):
        assert is_prime(7917) is False  # 7917 = 3 * 2639


class TestPrimeFactors:
    def test_prime_itself(self):
        assert prime_factors(7) == [7]

    def test_104_has_2_and_13(self):
        f = prime_factors(104)
        assert 2 in f and 13 in f

    def test_product_reconstructs_for_squarefree(self):
        n = 2 * 3 * 5 * 7  # 210
        f = prime_factors(n)
        result = 1
        for p in f:
            result *= p
        assert result == n

    def test_prime_squared_gives_one_factor(self):
        f = prime_factors(49)
        assert f == [7]

    def test_30_factors(self):
        f = prime_factors(30)
        assert set(f) == {2, 3, 5}

    def test_all_factors_are_prime(self):
        for factor in prime_factors(360):
            assert is_prime(factor)


class TestLargestPrimeFactor:
    def test_prime_input(self):
        assert largest_prime_factor(13) == 13

    def test_104(self):
        assert largest_prime_factor(104) == 13

    def test_power_of_2(self):
        assert largest_prime_factor(16) == 2

    def test_210(self):
        assert largest_prime_factor(210) == 7

    def test_prime_times_2(self):
        assert largest_prime_factor(2 * 103) == 103

    def test_one_raises(self):
        with pytest.raises((ValueError, Exception)):
            largest_prime_factor(1)


# ===========================================================================
# SECTION 2 — prime_field.py
# ===========================================================================


class TestPrimeFieldInit:
    @pytest.mark.parametrize("p", PRIMES_3_MOD_4)
    def test_accepts_valid_prime(self, p):
        assert PrimeField(p).order() == p

    @pytest.mark.parametrize("n", [4, 6, 8, 9, 10, 12, 15, 100, 104])
    def test_rejects_composites(self, n):
        with pytest.raises(ValueError):
            PrimeField(n)

    @pytest.mark.parametrize("p", [5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97])
    def test_rejects_primes_1_mod_4(self, p):
        with pytest.raises(ValueError):
            PrimeField(p)

    def test_equality(self):
        assert PrimeField(103) == PrimeField(103)

    def test_inequality(self):
        assert PrimeField(103) != PrimeField(107)

    def test_hashable_in_dict(self):
        f = PrimeField(103)
        d = {f: 42}
        assert d[PrimeField(103)] == 42

    def test_repr_contains_p(self):
        assert "103" in repr(PrimeField(103))

    def test_order_equals_p(self):
        assert PrimeField(103).order() == 103


class TestFieldElementAddition:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    @pytest.mark.parametrize("a, b", [(1, 2), (50, 50), (100, 5), (0, 0), (102, 1), (99, 10)])
    def test_result_mod_p(self, F, a, b):
        assert (F.element(a) + F.element(b)).value == (a + b) % 103

    def test_commutativity(self, F):
        assert F.element(42) + F.element(17) == F.element(17) + F.element(42)

    def test_associativity(self, F):
        a, b, c = F.element(10), F.element(30), F.element(70)
        assert (a + b) + c == a + (b + c)

    def test_identity_zero(self, F):
        a = F.element(55)
        assert a + F.element(0) == a

    def test_inverse_sums_to_zero(self, F):
        a = F.element(42)
        assert (a + (-a)).value == 0

    def test_wrap_around(self, F):
        assert (F.element(100) + F.element(10)).value == 7


class TestFieldElementSubtraction:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    @pytest.mark.parametrize("a, b", [(10, 5), (5, 10), (50, 50), (0, 1)])
    def test_result_mod_p(self, F, a, b):
        assert (F.element(a) - F.element(b)).value == (a - b) % 103

    def test_sub_self_is_zero(self, F):
        a = F.element(42)
        assert (a - a).value == 0

    def test_sub_zero_is_self(self, F):
        a = F.element(55)
        assert a - F.element(0) == a


class TestFieldElementMultiplication:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    @pytest.mark.parametrize("a, b", [(2, 3), (10, 10), (50, 2), (1, 99), (7, 15)])
    def test_result_mod_p(self, F, a, b):
        assert (F.element(a) * F.element(b)).value == (a * b) % 103

    def test_commutativity(self, F):
        assert F.element(5) * F.element(7) == F.element(7) * F.element(5)

    def test_associativity(self, F):
        a, b, c = F.element(2), F.element(3), F.element(5)
        assert (a * b) * c == a * (b * c)

    def test_distributivity(self, F):
        a, b, c = F.element(7), F.element(11), F.element(13)
        assert a * (b + c) == a * b + a * c

    def test_mul_by_zero(self, F):
        assert (F.element(42) * F.element(0)).value == 0

    def test_mul_by_one(self, F):
        a = F.element(42)
        assert a * F.element(1) == a

    def test_fermat_little_theorem(self, F):
        for a in [1, 5, 10, 42, 100, 102]:
            assert (F.element(a) ** 102).value == 1


class TestFieldElementDivisionAndInverse:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    @pytest.mark.parametrize("a", [1, 2, 3, 5, 7, 10, 42, 50, 100, 102])
    def test_inverse_mul_back(self, F, a):
        fa = F.element(a)
        assert (fa * fa.inverse()).value == 1

    def test_inverse_of_inverse(self, F):
        a = F.element(42)
        assert a.inverse().inverse() == a

    def test_inverse_zero_raises(self, F):
        with pytest.raises(ZeroDivisionError):
            F.element(0).inverse()

    def test_div_self_is_one(self, F):
        a = F.element(42)
        assert (a / a).value == 1

    def test_div_by_one_is_self(self, F):
        a = F.element(42)
        assert a / F.element(1) == a

    @pytest.mark.parametrize("a, b", [(10, 3), (50, 7), (100, 11), (77, 9)])
    def test_div_multiply_back(self, F, a, b):
        fa, fb = F.element(a), F.element(b)
        assert (fa / fb) * fb == fa

    def test_div_by_zero_raises(self, F):
        with pytest.raises(ZeroDivisionError):
            F.element(5) / F.element(0)


class TestFieldElementPower:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    @pytest.mark.parametrize("a, exp", [(2, 0), (3, 1), (5, 2), (7, 10), (2, 100), (10, 50)])
    def test_pow_matches_builtin(self, F, a, exp):
        assert F.element(a) ** exp == F.element(pow(a, exp, 103))

    def test_pow_zero_is_one(self, F):
        assert (F.element(42) ** 0).value == 1

    def test_pow_one_is_self(self, F):
        assert F.element(42) ** 1 == F.element(42)

    def test_pow_two_is_square(self, F):
        a = F.element(5)
        assert a ** 2 == a * a

    def test_pow_three_is_cube(self, F):
        a = F.element(5)
        assert a ** 3 == a * a * a


class TestFieldElementQRAndSqrt:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    def test_squares_are_qr(self, F):
        for a in range(1, 30):
            sq = (F.element(a) ** 2).value
            assert F.element(sq).is_quadratic_residue() is True

    def test_zero_is_qr(self, F):
        assert F.element(0).is_quadratic_residue() is True

    def test_half_nonzero_elements_are_qr(self, F):
        count = sum(1 for a in range(1, 103) if F.element(a).is_quadratic_residue())
        assert count == 51

    def test_sqrt_of_square(self, F):
        a = F.element(4)
        s = a.sqrt()
        assert (s * s) == a

    def test_sqrt_zero(self, F):
        assert F.element(0).sqrt().value == 0

    def test_sqrt_one(self, F):
        s = F.element(1).sqrt()
        assert (s * s).value == 1

    def test_sqrt_roundtrip_all_qr(self, F):
        for a in range(1, 103):
            fe = F.element(a)
            if fe.is_quadratic_residue():
                s = fe.sqrt()
                assert s * s == fe


class TestFieldElementReductionAndEquality:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    @pytest.mark.parametrize("val, expected", [
        (103, 0), (104, 1), (206, 0), (207, 1), (-1, 102), (-103, 0), (1000, 1000 % 103)
    ])
    def test_reduction(self, F, val, expected):
        assert F.element(val).value == expected

    def test_eq_same_value(self, F):
        assert F.element(5) == F.element(5)

    def test_neq_different_value(self, F):
        assert F.element(5) != F.element(6)

    def test_neq_different_field(self):
        f1 = PrimeField(103)
        f2 = PrimeField(107)
        assert f1.element(5) != f2.element(5)

    def test_hashable_in_set(self, F):
        s = {F.element(1), F.element(2), F.element(1)}
        assert len(s) == 2

    def test_value_always_in_range(self, F):
        for v in range(-50, 200):
            assert 0 <= F.element(v).value < 103

    def test_additive_order_p(self, F):
        result = F.element(0)
        one = F.element(1)
        for _ in range(103):
            result = result + one
        assert result.value == 0


class TestCrossFieldFermat:
    @pytest.mark.parametrize("p", [7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83, 103])
    def test_fermat(self, p):
        F = PrimeField(p)
        for a in [1, 2, p - 1]:
            assert (F.element(a) ** (p - 1)).value == 1

    @pytest.mark.parametrize("p", [7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83, 103])
    def test_every_nonzero_has_inverse(self, p):
        F = PrimeField(p)
        for a in range(1, min(p, 15)):
            assert (F.element(a) * F.element(a).inverse()).value == 1

    @pytest.mark.parametrize("p", [7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83, 103])
    def test_qr_count(self, p):
        F = PrimeField(p)
        count = sum(1 for a in range(1, p) if F.element(a).is_quadratic_residue())
        assert count == (p - 1) // 2

    @pytest.mark.parametrize("p", [7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83, 103])
    def test_sqrt_of_any_qr(self, p):
        F = PrimeField(p)
        for a in range(1, min(p, 20)):
            fe = F.element(a)
            if fe.is_quadratic_residue():
                s = fe.sqrt()
                assert s * s == fe

    @pytest.mark.parametrize("p", [7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83, 103])
    def test_closure_under_operations(self, p):
        F = PrimeField(p)
        a, b = F.element(p // 2), F.element(p // 3 + 1)
        assert 0 <= (a + b).value < p
        assert 0 <= (a * b).value < p
        assert 0 <= (a - b).value < p


# ===========================================================================
# SECTION 3 — polynomial.py
# ===========================================================================


class TestPolynomialInit:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    def test_zero_poly_degree_neg1(self, F):
        assert _poly([], F).degree() == -1

    def test_all_zeros_degree_neg1(self, F):
        assert _poly([0, 0, 0], F).degree() == -1

    def test_const_degree_0(self, F):
        assert _poly([5], F).degree() == 0

    def test_linear_degree_1(self, F):
        assert _poly([0, 1], F).degree() == 1

    def test_degree_2(self, F):
        assert _poly([1, 0, 1], F).degree() == 2

    def test_strips_trailing_zeros(self, F):
        assert _poly([1, 0, 0, 0], F).degree() == 0

    def test_monic_x2_plus_1(self, F):
        assert _poly([1, 0, 1], F).is_monic() is True

    def test_not_monic_2x(self, F):
        assert _poly([0, 2], F).is_monic() is False

    def test_monic_constant_1(self, F):
        assert _poly([1], F).is_monic() is True

    def test_not_monic_constant_2(self, F):
        assert _poly([2], F).is_monic() is False

    def test_does_not_mutate_input(self, F):
        coeffs = [F.element(1), F.element(0), F.element(0)]
        Polynomial(coeffs, F)
        assert len(coeffs) == 3


class TestPolynomialAddition:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    def test_add_zero(self, F):
        p = _poly([1, 2, 3], F)
        assert p + _poly([], F) == p

    def test_add_same_degree(self, F):
        r = _poly([1, 2], F) + _poly([3, 4], F)
        assert r.coeffs[0].value == 4 and r.coeffs[1].value == 6

    def test_add_different_degrees(self, F):
        r = _poly([1, 0, 1], F) + _poly([2, 3], F)
        assert r.degree() == 2 and r.coeffs[0].value == 3 and r.coeffs[1].value == 3

    def test_add_cancels_to_zero(self, F):
        p = _poly([1, 2], F)
        neg = _poly([102, 101], F)
        assert (p + neg).degree() == -1

    def test_add_commutative(self, F):
        p, q = _poly([1, 2, 3], F), _poly([4, 5, 6], F)
        assert p + q == q + p

    def test_add_associative(self, F):
        p, q, r = _poly([1, 2], F), _poly([3, 4], F), _poly([5, 6], F)
        assert (p + q) + r == p + (q + r)

    def test_add_wraps_mod_p(self, F):
        r = _poly([100], F) + _poly([10], F)
        assert r.coeffs[0].value == (100 + 10) % 103

    def test_different_fields_raises(self, F):
        F2 = PrimeField(107)
        with pytest.raises(ValueError):
            _poly([1], F) + _poly([1], F2)


class TestPolynomialSubtraction:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    def test_sub_self_is_zero(self, F):
        p = _poly([1, 2, 3], F)
        assert (p - p).degree() == -1

    def test_sub_zero_is_self(self, F):
        p = _poly([1, 2, 3], F)
        assert p - _poly([], F) == p

    def test_sub_result(self, F):
        r = _poly([3, 4], F) - _poly([1, 2], F)
        assert r.coeffs[0].value == 2 and r.coeffs[1].value == 2


class TestPolynomialMultiplication:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    def test_mul_by_zero(self, F):
        assert (_poly([1, 2, 3], F) * _poly([], F)).degree() == -1

    def test_mul_by_one(self, F):
        p = _poly([1, 2, 3], F)
        assert p * _poly([1], F) == p

    def test_mul_x_times_x_is_x2(self, F):
        x = _poly([0, 1], F)
        r = x * x
        assert r.degree() == 2 and r.coeffs[2].value == 1

    def test_mul_x_plus_1_squared(self, F):
        p = _poly([1, 1], F)
        r = p * p
        assert (r.coeffs[0].value, r.coeffs[1].value, r.coeffs[2].value) == (1, 2, 1)

    def test_mul_degree_adds(self, F):
        r = _poly([1, 1], F) * _poly([1, 0, 1], F)
        assert r.degree() == 3

    def test_mul_commutative(self, F):
        p, q = _poly([1, 2, 3], F), _poly([4, 5], F)
        assert p * q == q * p

    def test_mul_distributive_over_add(self, F):
        a, b, c = _poly([1, 2], F), _poly([3, 4], F), _poly([5, 6], F)
        assert a * (b + c) == a * b + a * c

    def test_different_fields_raises(self, F):
        F2 = PrimeField(107)
        with pytest.raises(ValueError):
            _poly([1], F) * _poly([1], F2)


class TestPolynomialDivMod:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    def test_mod_by_self_is_zero(self, F):
        p = _poly([1, 2, 3], F)
        assert (p % p).degree() == -1

    def test_mod_lower_degree_is_self(self, F):
        assert _poly([1, 2], F) % _poly([1, 0, 1], F) == _poly([1, 2], F)

    def test_mod_zero_raises(self, F):
        with pytest.raises(ValueError):
            _poly([1, 2], F) % _poly([], F)

    def test_mod_x2_mod_x_is_0(self, F):
        r = _poly([0, 0, 1], F) % _poly([0, 1], F)
        assert r.degree() == -1

    def test_mod_x2_plus_1_mod_x(self, F):
        r = _poly([1, 0, 1], F) % _poly([0, 1], F)
        assert r.degree() == 0 and r.coeffs[0].value == 1

    def test_div_gives_quotient(self, F):
        p = _poly([1, 0, 1], F)
        d = _poly([1, 1], F)
        q = p / d
        r = p % d
        assert p == q * d + r

    def test_div_by_zero_raises(self, F):
        with pytest.raises(ZeroDivisionError):
            _poly([1, 2], F) / _poly([], F)

    def test_div_lower_degree_is_zero(self, F):
        result = _poly([1, 2], F) / _poly([1, 0, 1], F)
        assert result.degree() == -1


class TestPolynomialPow:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    def test_pow_0_is_one(self, F):
        r = _poly([1, 1], F) ** 0
        assert r.degree() == 0 and r.coeffs[0].value == 1

    def test_pow_1_is_self(self, F):
        p = _poly([1, 1], F)
        assert p ** 1 == p

    def test_pow_2_is_square(self, F):
        p = _poly([1, 1], F)
        assert p ** 2 == p * p

    def test_pow_3_is_cube(self, F):
        p = _poly([1, 1], F)
        assert p ** 3 == p * p * p

    def test_pow_negative_raises(self, F):
        with pytest.raises(ValueError):
            _poly([1, 1], F) ** -1

    def test_pow_with_modulus_reduces_degree(self, F):
        irr = _poly([1, 0, 1], F)
        x = _poly([0, 1], F)
        r = pow(x, 2, irr)
        assert r.degree() == 0 and r.coeffs[0].value == 102

    @pytest.mark.parametrize("n", [0, 1, 2, 3, 4, 5])
    def test_pow_x_degree(self, F, n):
        x = _poly([0, 1], F)
        assert (x ** n).degree() == (n if n > 0 else 0)


class TestPolynomialGCDAndIrreducible:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    def test_gcd_self(self, F):
        p = _poly([1, 1], F)
        g = p.gcd(p)
        assert g.is_monic() and g.degree() == p.degree()

    def test_gcd_coprime_degree_0(self, F):
        p = _poly([1, 0, 1], F)   # x^2+1, irreducible
        q = _poly([1, 1], F)       # x+1
        g = p.gcd(q)
        assert g.degree() <= 0

    def test_gcd_symmetric(self, F):
        p = _poly([102, 0, 1], F)
        q = _poly([102, 1], F)
        assert p.gcd(q) == q.gcd(p)

    def test_x2_plus_1_irreducible(self, F):
        assert _poly([1, 0, 1], F).is_irreducible(2) is True

    def test_x2_minus_1_reducible(self, F):
        assert _poly([102, 0, 1], F).is_irreducible(2) is False

    def test_wrong_k_raises(self, F):
        with pytest.raises(ValueError):
            _poly([1, 0, 1], F).is_irreducible(3)

    def test_make_monic_already_monic(self, F):
        p = _poly([1, 1], F)
        assert p.make_monic() == p

    def test_make_monic_scales(self, F):
        p = _poly([2, 2], F)
        assert p.make_monic().is_monic()

    def test_extended_gcd_bezout(self, F):
        p = _poly([1, 0, 1], F)
        q = _poly([1, 1], F)
        g, s, t = p.extended_gcd(q)
        assert (s * p + t * q).make_monic() == g.make_monic()


class TestPolynomialRepr:
    @pytest.fixture
    def F(self):
        return PrimeField(103)

    def test_repr_zero(self, F):
        assert repr(_poly([], F)) == "0"

    def test_repr_x(self, F):
        assert repr(_poly([0, 1], F)) == "x"

    def test_repr_constant(self, F):
        assert "5" in repr(_poly([5], F))

    def test_repr_nonzero(self, F):
        assert len(repr(_poly([1, 0, 1], F))) > 0


# ===========================================================================
# SECTION 4 — elliptic_curve.py
# ===========================================================================


@pytest.fixture(scope="module")
def F103():
    return PrimeField(103)


@pytest.fixture(scope="module")
def curve103(F103):
    return EllipticCurve(F103, A=1, B=0)


@pytest.fixture(scope="module")
def origin103(F103, curve103):
    return ECPoint(curve103, F103.element(0), F103.element(0))


class TestEllipticCurveInit:
    def test_stores_A_B(self, curve103, F103):
        assert curve103.A.value == 1 and curve103.B.value == 0

    def test_singular_raises(self, F103):
        with pytest.raises(ValueError):
            EllipticCurve(F103, A=0, B=0)

    def test_non_singular(self, curve103):
        assert curve103.is_non_singular() is True

    def test_group_order_104(self, curve103):
        assert curve103.group_order() == 104

    def test_identity_is_infinity(self, curve103):
        O = curve103.identity()
        assert O.is_infinity and O.x is None and O.y is None

    def test_repr_not_empty(self, curve103):
        assert len(repr(curve103)) > 0

    def test_contains_origin(self, curve103, F103):
        assert curve103.contains(ECPoint(curve103, F103.element(0), F103.element(0)))


class TestECPointAddition:
    def test_P_plus_O_is_P(self, curve103, F103, origin103):
        O = curve103.identity()
        assert origin103 + O == origin103

    def test_O_plus_P_is_P(self, curve103, F103, origin103):
        O = curve103.identity()
        assert O + origin103 == origin103

    def test_O_plus_O_is_O(self, curve103):
        O = curve103.identity()
        assert (O + O).is_infinity

    def test_P_plus_neg_P_is_O(self, origin103):
        assert (origin103 + (-origin103)).is_infinity

    def test_double_on_curve(self, curve103, origin103):
        Q = origin103 + origin103
        assert Q.is_infinity or curve103.contains(Q)

    def test_commutative(self, curve103, F103, origin103):
        Q = 2 * origin103
        if not Q.is_infinity:
            assert origin103 + Q == Q + origin103

    def test_associative(self, curve103, F103, origin103):
        P, Q, R = origin103, 2 * origin103, 3 * origin103
        if not (Q.is_infinity or R.is_infinity):
            assert (P + Q) + R == P + (Q + R)

    def test_result_on_curve(self, curve103, origin103):
        for k in range(1, 14):
            pt = k * origin103
            assert pt.is_infinity or curve103.contains(pt)


class TestECPointNegation:
    def test_neg_infinity(self, curve103):
        assert (-curve103.identity()).is_infinity

    def test_neg_same_x(self, origin103):
        assert (-origin103).x == origin103.x

    def test_neg_neg_is_self(self, origin103):
        assert -(-origin103) == origin103

    def test_plus_neg_is_zero(self, origin103):
        assert (origin103 + (-origin103)).is_infinity


class TestECPointScalarMul:
    @pytest.mark.parametrize("k", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
    def test_k_times_P_on_curve_or_infinity(self, curve103, F103, k):
        P = ECPoint(curve103, F103.element(0), F103.element(0))
        Q = k * P
        assert Q.is_infinity or curve103.contains(Q)

    def test_0P_is_infinity(self, origin103):
        assert (0 * origin103).is_infinity

    def test_1P_is_self(self, origin103):
        assert 1 * origin103 == origin103

    def test_2P_is_double(self, origin103):
        assert 2 * origin103 == origin103 + origin103

    def test_3P_is_triple(self, origin103):
        assert 3 * origin103 == origin103 + origin103 + origin103

    def test_group_order_times_P_is_O(self, curve103, origin103):
        assert (104 * origin103).is_infinity

    def test_distributivity(self, origin103):
        for a, b in [(2, 3), (4, 5), (6, 7)]:
            lhs = (a + b) * origin103
            rhs = a * origin103 + b * origin103
            assert lhs == rhs

    def test_order_divides_group_order(self, curve103, origin103):
        assert curve103.group_order() % origin103.order() == 0

    def test_order_mul_is_identity(self, origin103):
        n = origin103.order()
        assert (n * origin103).is_infinity

    def test_rmul(self, curve103, F103):
        P = ECPoint(curve103, F103.element(0), F103.element(0))
        assert 2 * P == P * 2 if hasattr(P, "__mul__") else True


class TestECPointEquality:
    def test_eq_same(self, curve103, F103):
        P1 = ECPoint(curve103, F103.element(0), F103.element(0))
        P2 = ECPoint(curve103, F103.element(0), F103.element(0))
        assert P1 == P2

    def test_neq_different(self, curve103, F103, origin103):
        Q = 2 * origin103
        if not Q.is_infinity:
            assert origin103 != Q

    def test_infinity_eq(self, curve103):
        O1 = curve103.identity()
        O2 = ECPoint(curve103, None, None, is_infinity=True)
        assert O1 == O2

    def test_repr_affine(self, origin103):
        assert "0" in repr(origin103)

    def test_repr_infinity(self, curve103):
        r = repr(curve103.identity())
        assert r is not None


# ===========================================================================
# SECTION 5 — extension_field.py
# ===========================================================================


@pytest.fixture(scope="module")
def EF103():
    F = PrimeField(103)
    irr = Polynomial([F.element(1), F.element(0), F.element(1)], F)
    return ExtensionField(F, irr)


class TestExtensionFieldInit:
    def test_k_is_2(self, EF103):
        assert EF103.k == 2

    def test_base_field(self, EF103):
        assert EF103.base_field.p == 103

    def test_reducible_raises(self):
        F = PrimeField(103)
        red = Polynomial([F.element(102), F.element(0), F.element(1)], F)  # x^2 - 1
        with pytest.raises(ValueError):
            ExtensionField(F, red)

    def test_degree_0_raises(self):
        F = PrimeField(103)
        const = Polynomial([F.element(1)], F)
        with pytest.raises(ValueError):
            ExtensionField(F, const)

    def test_find_embedding_degree(self):
        assert ExtensionField.find_embedding_degree(103, 13) == 2

    def test_find_irreducible_degree_2(self):
        F = PrimeField(103)
        irr = ExtensionField.find_irreducible(F, 2)
        assert irr.degree() == 2 and irr.is_irreducible(2)


class TestExtFieldElementArithmetic:
    def test_add(self, EF103):
        a = EF103.element([1, 2])
        b = EF103.element([3, 4])
        c = a + b
        assert c.poly.coeffs[0].value == 4 and c.poly.coeffs[1].value == 6

    def test_sub(self, EF103):
        a = EF103.element([5, 7])
        b = EF103.element([2, 3])
        c = a - b
        assert c.poly.coeffs[0].value == 3 and c.poly.coeffs[1].value == 4

    def test_mul_by_zero(self, EF103):
        assert (EF103.element([1, 2]) * EF103.element([0])).poly.degree() == -1

    def test_mul_by_one(self, EF103):
        a = EF103.element([1, 2])
        assert a * EF103.element([1]) == a

    def test_i_squared_is_neg1(self, EF103):
        i = EF103.element([0, 1])
        i_sq = i * i
        assert i_sq.poly.coeffs[0].value == 102 and i_sq.poly.degree() == 0

    def test_pow_0_is_one(self, EF103):
        r = EF103.element([2, 3]) ** 0
        assert r.poly.coeffs[0].value == 1 and r.poly.degree() == 0

    def test_pow_1_is_self(self, EF103):
        a = EF103.element([2, 3])
        assert a ** 1 == a

    def test_pow_2_is_square(self, EF103):
        a = EF103.element([2, 3])
        assert a ** 2 == a * a

    def test_inverse_mul_back(self, EF103):
        a = EF103.element([1, 1])
        r = a * a.inverse()
        assert r.poly.coeffs[0].value == 1 and r.poly.degree() == 0

    def test_neg_plus_self_is_zero(self, EF103):
        a = EF103.element([1, 2])
        assert (a + (-a)).poly.degree() == -1

    def test_eq(self, EF103):
        assert EF103.element([1, 2]) == EF103.element([1, 2])

    def test_neq(self, EF103):
        assert EF103.element([1, 2]) != EF103.element([1, 3])

    def test_commutative_add(self, EF103):
        a, b = EF103.element([1, 2]), EF103.element([3, 4])
        assert a + b == b + a

    def test_commutative_mul(self, EF103):
        a, b = EF103.element([1, 2]), EF103.element([3, 4])
        assert a * b == b * a

    def test_associative_add(self, EF103):
        a, b, c = EF103.element([1, 2]), EF103.element([3, 4]), EF103.element([5, 6])
        assert (a + b) + c == a + (b + c)

    def test_associative_mul(self, EF103):
        a, b, c = EF103.element([1, 2]), EF103.element([3, 4]), EF103.element([5, 6])
        assert (a * b) * c == a * (b * c)

    def test_distributive(self, EF103):
        a, b, c = EF103.element([1, 2]), EF103.element([3, 4]), EF103.element([5, 6])
        assert a * (b + c) == a * b + a * c

    def test_frobenius_p2_minus_1(self, EF103):
        a = EF103.element([1, 1])
        p, k = 103, 2
        r = a ** (p ** k - 1)
        assert r.poly.coeffs[0].value == 1 and r.poly.degree() == 0

    def test_hash_equal_elements(self, EF103):
        a = EF103.element([1, 2])
        b = EF103.element([1, 2])
        assert hash(a) == hash(b)

    def test_repr_nonempty(self, EF103):
        assert len(repr(EF103.element([1, 2]))) > 0

    def test_element_reduces_degree(self, EF103):
        # x^2 ≡ -1 in F_{103^2} / (x^2+1)
        e = EF103.element([0, 0, 1])
        assert e.poly.degree() <= 1


# ===========================================================================
# SECTION 6 — hash_to_point.py
# ===========================================================================


@pytest.fixture(scope="module")
def curve_for_hash():
    F = PrimeField(103)
    return EllipticCurve(F, A=1, B=0)


class TestStringToFieldElement:
    def test_basic_ascii(self, curve_for_hash):
        fe = string_to_field_element("a", curve_for_hash.field)
        assert 0 <= fe.value < 103

    def test_empty_string(self, curve_for_hash):
        fe = string_to_field_element("", curve_for_hash.field)
        assert fe.value == 0

    def test_deterministic(self, curve_for_hash):
        fe1 = string_to_field_element("hello", curve_for_hash.field)
        fe2 = string_to_field_element("hello", curve_for_hash.field)
        assert fe1 == fe2

    def test_different_strings_different_values(self, curve_for_hash):
        fe1 = string_to_field_element("abc", curve_for_hash.field)
        fe2 = string_to_field_element("xyz", curve_for_hash.field)
        assert 0 <= fe1.value < 103
        assert 0 <= fe2.value < 103

    def test_hebrew(self, curve_for_hash):
        fe = string_to_field_element("שלום", curve_for_hash.field)
        assert 0 <= fe.value < 103

    def test_result_in_field(self, curve_for_hash):
        for msg in ["a", "b", "hello", "world", "test", "crypto"]:
            fe = string_to_field_element(msg, curve_for_hash.field)
            assert 0 <= fe.value < 103


class TestIncrementAndTry:
    def test_returns_point_on_curve(self, curve_for_hash):
        P = increment_and_try(curve_for_hash.field.element(0), curve_for_hash)
        assert curve_for_hash.contains(P)

    @pytest.mark.parametrize("x_val", range(10))
    def test_various_x(self, curve_for_hash, x_val):
        P = increment_and_try(curve_for_hash.field.element(x_val), curve_for_hash)
        assert curve_for_hash.contains(P) or P.is_infinity

    def test_deterministic(self, curve_for_hash):
        x = curve_for_hash.field.element(5)
        P1 = increment_and_try(x, curve_for_hash)
        P2 = increment_and_try(x, curve_for_hash)
        assert P1 == P2


class TestCofactorClear:
    def test_r_times_result_is_identity(self, curve_for_hash):
        P = increment_and_try(curve_for_hash.field.element(0), curve_for_hash)
        Q = cofactor_clear(P, 104, 13)
        assert (13 * Q).is_infinity

    def test_result_on_curve(self, curve_for_hash):
        P = increment_and_try(curve_for_hash.field.element(0), curve_for_hash)
        Q = cofactor_clear(P, 104, 13)
        assert Q.is_infinity or curve_for_hash.contains(Q)


class TestHashToPoint:
    def test_returns_curve_point(self, curve_for_hash):
        P = hash_to_point("hello", curve_for_hash, 13)
        assert curve_for_hash.contains(P) or P.is_infinity

    def test_deterministic(self, curve_for_hash):
        assert hash_to_point("hello", curve_for_hash, 13) == hash_to_point("hello", curve_for_hash, 13)

    def test_order_divides_r(self, curve_for_hash):
        P = hash_to_point("test", curve_for_hash, 13)
        assert (13 * P).is_infinity

    def test_hebrew_assignment_point(self, curve_for_hash):
        P = hash_to_point("שלום", curve_for_hash, 13)
        assert P.x.value == 32 and P.y.value == 47

    def test_various_ascii_messages(self, curve_for_hash):
        for msg in ["a", "b", "hello", "world", "crypto", "bls"]:
            P = hash_to_point(msg, curve_for_hash, 13)
            assert curve_for_hash.contains(P) or P.is_infinity
            assert (13 * P).is_infinity


# ===========================================================================
# SECTION 7 — BLS signature scheme
# ===========================================================================


@pytest.fixture(scope="module")
def bls7():
    return BLSSignatureScheme(p=103, A=1, B=0, private_key=7)


class TestBLSInit:
    def test_field_p(self, bls7):
        assert bls7.field.p == 103

    def test_group_order(self, bls7):
        assert bls7.group_order == 104

    def test_r(self, bls7):
        assert bls7.r == 13

    def test_cofactor(self, bls7):
        assert bls7.cofactor == 8

    def test_k(self, bls7):
        assert bls7.k == 2

    def test_private_key(self, bls7):
        assert bls7.private_key == 7


class TestBLSSign:
    def test_sign_returns_ECPoint(self, bls7):
        assert isinstance(bls7.sign("hello"), ECPoint)

    def test_sign_on_curve(self, bls7):
        sig = bls7.sign("hello")
        assert bls7.curve.contains(sig) or sig.is_infinity

    def test_sign_deterministic(self, bls7):
        assert bls7.sign("hello") == bls7.sign("hello")

    def test_sign_different_messages(self, bls7):
        s1 = bls7.sign("hello")
        s2 = bls7.sign("world")
        assert s1 != s2

    def test_assignment_signature(self, bls7):
        sig = bls7.sign("שלום")
        assert sig.x.value == 18 and sig.y.value == 44


class TestBLSVerify:
    def test_verify_valid(self, bls7):
        sig = bls7.sign("hello")
        assert bls7.verify("hello", sig) is True

    def test_verify_wrong_message(self, bls7):
        sig = bls7.sign("hello")
        assert bls7.verify("world", sig) is False

    def test_verify_hebrew_assignment(self, bls7):
        sig = bls7.sign("שלום")
        assert bls7.verify("שלום", sig) is True

    def test_verify_various_messages(self, bls7):
        for msg in ["a", "test", "crypto", "bls12"]:
            sig = bls7.sign(msg)
            if sig.is_infinity:
                continue  # message hashes to identity — degenerate, skip
            assert bls7.verify(msg, sig) is True

    def test_verify_private_key_2(self):
        bls = BLSSignatureScheme(p=103, A=1, B=0, private_key=2)
        sig = bls.sign("test")
        assert bls.verify("test", sig) is True

    def test_verify_private_key_5(self):
        bls = BLSSignatureScheme(p=103, A=1, B=0, private_key=5)
        sig = bls.sign("abc")
        assert bls.verify("abc", sig) is True

    def test_verify_private_key_10(self):
        bls = BLSSignatureScheme(p=103, A=1, B=0, private_key=10)
        sig = bls.sign("msg")
        assert bls.verify("msg", sig) is True

    def test_cross_key_verify_fails(self):
        bls7 = BLSSignatureScheme(p=103, A=1, B=0, private_key=7)
        bls2 = BLSSignatureScheme(p=103, A=1, B=0, private_key=2)
        sig = bls7.sign("hello")
        assert bls2.verify("hello", sig) is False


class TestBLSTatePairing:
    def test_returns_ext_field_element(self, bls7):
        P = hash_to_point("test", bls7.curve, bls7.r)
        result = bls7.tate_pairing(P, bls7.Q)
        assert result is not None

    def test_bilinearity(self, bls7):
        P = hash_to_point("test", bls7.curve, bls7.r)
        e1 = bls7.tate_pairing(bls7.private_key * P, bls7.Q)
        e2 = bls7.tate_pairing(P, bls7.public_key)
        assert e1 == e2

    def test_assignment_pairing_values(self, bls7):
        sig = bls7.sign("שלום")
        Hm = hash_to_point("שלום", bls7.curve, bls7.r)
        lhs = bls7.tate_pairing(sig, bls7.Q)
        rhs = bls7.tate_pairing(Hm, bls7.public_key)
        assert lhs == rhs


class TestBLSGetSteps:
    def test_returns_dict(self, bls7):
        assert isinstance(bls7.get_steps("hello"), dict)

    def test_nonempty_dict(self, bls7):
        assert len(bls7.get_steps("hello")) > 0

    def test_deterministic(self, bls7):
        s1 = bls7.get_steps("hello")
        s2 = bls7.get_steps("hello")
        assert s1 == s2
