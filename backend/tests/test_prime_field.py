"""Unit tests for app.crypto.prime_field — TDD style."""

import pytest
from app.crypto.prime_field import PrimeField, FieldElement


class TestPrimeField:
    """Tests for PrimeField."""

    def test_init_accepts_valid_prime_mod4(self, small_prime):
        field = PrimeField(small_prime)
        assert field.p == small_prime
        assert field.order() == small_prime

    def test_init_rejects_non_prime(self):
        with pytest.raises(ValueError):
            PrimeField(104)

    def test_init_rejects_prime_not_3_mod_4(self, invalid_prime_not_mod4):
        with pytest.raises(ValueError):
            PrimeField(invalid_prime_not_mod4)

    def test_element_reduces_mod_p(self, small_prime):
        field = PrimeField(small_prime)
        a = field.element(110)
        assert a.value == 7  # 110 mod 103 = 7

    def test_repr(self, small_prime):
        field = PrimeField(small_prime)
        assert "103" in repr(field)


class TestFieldElement:
    """Tests for FieldElement arithmetic in F_p."""

    @pytest.fixture
    def field(self, small_prime):
        return PrimeField(small_prime)

    def test_add(self, field):
        a, b = field.element(10), field.element(95)
        c = a + b
        assert c.value == (10 + 95) % field.p

    def test_sub(self, field):
        a, b = field.element(5), field.element(10)
        c = a - b
        assert c.value == (5 - 10) % field.p

    def test_mul(self, field):
        a, b = field.element(10), field.element(11)
        c = a * b
        assert c.value == (10 * 11) % field.p

    def test_truediv(self, field):
        a, b = field.element(5), field.element(7)
        c = a / b
        assert (c * b).value == a.value

    def test_neg(self, field):
        a = field.element(5)
        n = -a
        assert (a + n).value == 0

    def test_pow_zero(self, field):
        a = field.element(5)
        assert (a ** 0).value == 1

    def test_pow_positive(self, field):
        a = field.element(5)
        assert (a ** 3).value == pow(5, 3, field.p)

    def test_inverse(self, field):
        a = field.element(7)
        inv = a.inverse()
        assert (a * inv).value == 1

    def test_inverse_zero_raises(self, field):
        z = field.element(0)
        with pytest.raises(ZeroDivisionError):
            z.inverse()

    def test_eq(self, field):
        a = field.element(5)
        b = field.element(5)
        c = field.element(6)
        assert a == b
        assert a != c

    def test_different_field_element_not_equal(self, field):
        other_field = PrimeField(107)  # another prime 107 ≡ 3 mod 4
        a = field.element(5)
        b = other_field.element(5)
        assert a != b

    def test_is_quadratic_residue(self, field):
        # 4 is QR mod 103 (2^2 = 4)
        q = field.element(4)
        assert q.is_quadratic_residue() is True

    def test_sqrt(self, field):
        # 4 = 2^2
        q = field.element(4)
        s = q.sqrt()
        assert (s * s).value == 4

    def test_hash(self, field):
        a = field.element(5)
        b = field.element(5)
        assert hash(a) == hash(b)

    def test_repr(self, field):
        a = field.element(5)
        assert "5" in repr(a)
