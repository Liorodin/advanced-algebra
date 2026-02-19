"""Shared pytest fixtures for backend tests.

Provides common fixtures (e.g. prime field, curve) once implementations exist.
"""

import pytest


@pytest.fixture
def small_prime():
    """Prime p ≡ 3 (mod 4) for tests (e.g. 103)."""
    return 103


@pytest.fixture
def invalid_prime_not_mod4():
    """Prime that is not ≡ 3 (mod 4), e.g. 17."""
    return 17
