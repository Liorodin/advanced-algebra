"""Unit tests for app.crypto.utils — TDD style.

Tests define expected behavior; they will fail until implementations exist.
"""

from app.crypto.utils import (
    gcd,
    extended_gcd,
    is_prime,
    prime_factors,
    largest_prime_factor,
)


class TestGcd:
    """Tests for gcd(a, b)."""

    def test_gcd_positive(self):
        assert gcd(12, 8) == 4
        assert gcd(8, 12) == 4

    def test_gcd_coprime(self):
        assert gcd(17, 5) == 1
        assert gcd(35, 15) == 5

    def test_gcd_one_zero(self):
        assert gcd(0, 7) == 7
        assert gcd(7, 0) == 7

    def test_gcd_both_zero(self):
        assert gcd(0, 0) == 0

    def test_gcd_negative_treated_as_positive(self):
        # Euclid's algorithm typically uses abs; behavior may vary
        assert gcd(-12, 8) in (4, -4)
        assert gcd(12, -8) in (4, -4)


class TestExtendedGcd:
    """Tests for extended_gcd(a, b) -> (g, x, y) where a*x + b*y = g."""

    def test_extended_gcd_example(self):
        g, x, y = extended_gcd(35, 15)
        assert g == 5
        assert 35 * x + 15 * y == g

    def test_extended_gcd_coprime(self):
        g, x, y = extended_gcd(17, 5)
        assert g == 1
        assert 17 * x + 5 * y == 1

    def test_extended_gcd_inverse_mod(self):
        # 7^{-1} mod 103 = 59 (or similar)
        g, x, _ = extended_gcd(7, 103)
        assert g == 1
        assert (7 * x) % 103 == 1


class TestIsPrime:
    """Tests for is_prime(n)."""

    def test_is_prime_small_primes(self):
        assert is_prime(2) is True
        assert is_prime(3) is True
        assert is_prime(103) is True

    def test_is_prime_composite(self):
        assert is_prime(104) is False
        assert is_prime(4) is False
        assert is_prime(1) is False

    def test_is_prime_zero_and_negative(self):
        assert is_prime(0) is False
        assert is_prime(-7) is False


class TestPrimeFactors:
    """Tests for prime_factors(n)."""

    def test_prime_factors_composite(self):
        assert sorted(prime_factors(12)) == [2, 3]
        assert sorted(prime_factors(24)) == [2, 3]

    def test_prime_factors_prime(self):
        assert prime_factors(13) == [13]
        assert prime_factors(2) == [2]

    def test_prime_factors_one(self):
        assert prime_factors(1) == []


class TestLargestPrimeFactor:
    """Tests for largest_prime_factor(n)."""

    def test_largest_prime_factor_example(self):
        assert largest_prime_factor(104) == 13

    def test_largest_prime_factor_prime(self):
        assert largest_prime_factor(13) == 13

    def test_largest_prime_factor_power_of_two(self):
        assert largest_prime_factor(16) == 2
