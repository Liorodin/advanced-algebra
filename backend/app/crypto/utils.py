"""Shared mathematical utilities for BLS signature scheme.

This module provides fundamental number-theoretic functions used
throughout the cryptographic pipeline.
"""


def gcd(a: int, b: int) -> int:
    """Compute the greatest common divisor of a and b using Euclid's algorithm.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        The greatest common divisor gcd(a, b).

    Examples:
        >>> gcd(12, 8)
        4
        >>> gcd(17, 5)
        1
    """
    raise NotImplementedError("gcd: Implement Euclid's algorithm")


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean algorithm.

    Finds integers g, x, y such that a*x + b*y = g = gcd(a, b).
    Used primarily for computing modular inverses: if gcd(a, p) = 1,
    then a^{-1} mod p = x mod p.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        Tuple (g, x, y) where g = gcd(a, b) and a*x + b*y = g.

    Examples:
        >>> extended_gcd(35, 15)
        (5, 1, -2)
    """
    raise NotImplementedError("extended_gcd: Implement the extended Euclidean algorithm")


def is_prime(n: int) -> bool:
    """Test whether n is a prime number.

    Use trial division up to sqrt(n) or a more sophisticated method.
    Must handle edge cases: n <= 1 is not prime, n = 2 is prime.

    Args:
        n: Integer to test.

    Returns:
        True if n is prime, False otherwise.

    Examples:
        >>> is_prime(103)
        True
        >>> is_prime(104)
        False
    """
    raise NotImplementedError("is_prime: Implement primality test (trial division is fine)")


def prime_factors(n: int) -> list[int]:
    """Find all prime factors of n (with multiplicity).

    Used by Rabin's irreducibility test which needs the distinct prime
    factors of the polynomial degree k.

    Args:
        n: Positive integer to factorize.

    Returns:
        List of prime factors (may contain duplicates).

    Examples:
        >>> prime_factors(12)
        [2, 2, 3]
        >>> prime_factors(13)
        [13]
    """
    raise NotImplementedError("prime_factors: Implement trial division factorization")


def largest_prime_factor(n: int) -> int:
    """Find the largest prime factor of n.

    In the BLS scheme, we compute |G| = |E(F_p)| and then find its
    largest prime factor r, which becomes the order of the subgroup
    we work in.

    Args:
        n: Positive integer.

    Returns:
        The largest prime factor of n.

    Examples:
        >>> largest_prime_factor(104)
        13
    """
    raise NotImplementedError("largest_prime_factor: Use prime_factors and return max")
