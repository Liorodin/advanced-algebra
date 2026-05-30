"""Shared pytest fixtures and CLI options for backend tests."""

import os
import pytest


def pytest_addoption(parser):
    group = parser.getgroup("random-primes", "Random prime test configuration")
    group.addoption(
        "--prime-limit",
        type=int,
        default=None,
        metavar="N",
        help="Upper bound for prime generation in test_random_primes (default: 400 or TEST_PRIME_LIMIT env var)",
    )
    group.addoption(
        "--n-primes",
        type=int,
        default=None,
        metavar="N",
        help="Number of random primes to sample in test_random_primes (default: 30 or TEST_N_PRIMES env var)",
    )
    group.addoption(
        "--test-seed",
        type=int,
        default=None,
        metavar="N",
        help="RNG seed for test_random_primes; omit for a fresh random seed (overrides TEST_SEED env var)",
    )


def pytest_configure(config):
    """Push CLI options into env vars before test modules are imported."""
    mapping = {
        "--prime-limit": "TEST_PRIME_LIMIT",
        "--n-primes":    "TEST_N_PRIMES",
        "--test-seed":   "TEST_SEED",
    }
    for opt, env in mapping.items():
        try:
            val = config.getoption(opt)
        except (ValueError, AttributeError):
            val = None
        if val is not None:
            os.environ[env] = str(val)


@pytest.fixture
def small_prime():
    """Prime p ≡ 3 (mod 4) for tests (e.g. 103)."""
    return 103


@pytest.fixture
def invalid_prime_not_mod4():
    """Prime that is not ≡ 3 (mod 4), e.g. 17."""
    return 17
