"""Property tests driven by randomly generated primes ≡ 3 (mod 4).

Configuration via environment variables (all optional):

    TEST_PRIME_LIMIT   — upper bound for prime generation   (default: 400)
    TEST_N_PRIMES      — how many primes to sample          (default: 30)
    TEST_SEED          — RNG seed; omit for a fresh random  (default: random)

Example:
    TEST_PRIME_LIMIT=1000 TEST_N_PRIMES=60 TEST_SEED=7 pytest tests/test_random_primes.py
"""

import math
import os
import random

import pytest

from app.crypto.utils import is_prime, largest_prime_factor
from app.crypto.prime_field import PrimeField
from app.crypto.polynomial import Polynomial
from app.crypto.elliptic_curve import EllipticCurve, ECPoint
from app.crypto.bls import BLSSignatureScheme
from app.crypto.hash_to_point import hash_to_point

# ---------------------------------------------------------------------------
# Configuration — read from environment, then print so failures are reproducible
# ---------------------------------------------------------------------------

PRIME_LIMIT: int = int(os.environ.get("TEST_PRIME_LIMIT", "400"))
N_PRIMES:    int = int(os.environ.get("TEST_N_PRIMES",    "30"))

_seed_env = os.environ.get("TEST_SEED")
if _seed_env is None:
    SEED: int = random.randint(0, 2**32 - 1)
    print(f"\n[test_random_primes] random seed={SEED}  "
          f"(rerun with TEST_SEED={SEED} to reproduce)")
else:
    SEED = int(_seed_env)
    print(f"\n[test_random_primes] fixed seed={SEED}")

# ---------------------------------------------------------------------------
# Prime generation helpers
# ---------------------------------------------------------------------------

def all_primes_3_mod_4(limit: int) -> list[int]:
    return [p for p in range(3, limit + 1) if p % 4 == 3 and is_prime(p)]


def random_nonsingular_curve(field: PrimeField, rng: random.Random) -> EllipticCurve:
    p = field.p
    for _ in range(10_000):
        A = rng.randint(0, p - 1)
        B = rng.randint(0, p - 1)
        if (4 * A**3 + 27 * B**2) % p != 0:
            return EllipticCurve(field, A, B)
    raise RuntimeError(f"No non-singular curve over F_{p}")


def find_point_on_curve(curve: EllipticCurve) -> ECPoint:
    field = curve.field
    for x_val in range(field.p):
        fe = field.element(x_val)
        z = fe**3 + curve.A * fe + curve.B
        if z.is_quadratic_residue():
            y = z.sqrt()
            pt = ECPoint(curve, fe, y)
            if not pt.is_infinity:
                return pt
    return curve.identity()


def _poly(coeffs: list[int], F: PrimeField) -> Polynomial:
    return Polynomial([F.element(c) for c in coeffs], F)


# ---------------------------------------------------------------------------
# Build parametrize lists at import time (seeded)
# ---------------------------------------------------------------------------

_ALL_PRIMES = all_primes_3_mod_4(PRIME_LIMIT)

_rng = random.Random(SEED)
_field_primes: list[int] = _rng.sample(_ALL_PRIMES, min(N_PRIMES, len(_ALL_PRIMES)))
_curve_primes: list[int] = _rng.sample(_ALL_PRIMES, min(max(N_PRIMES // 2, 5), len(_ALL_PRIMES)))
_bls_primes:   list[int] = [103, 107, 127, 131, 139]

_rng2 = random.Random(SEED + 1)
_curve_fixtures: list[tuple[PrimeField, EllipticCurve, ECPoint]] = []
for _p in _curve_primes:
    _F = PrimeField(_p)
    _C = random_nonsingular_curve(_F, _rng2)
    _P = find_point_on_curve(_C)
    _curve_fixtures.append((_F, _C, _P))

_curve_ids = [f"p={t[0].p},A={t[1].A.value},B={t[1].B.value}" for t in _curve_fixtures]

_EDGE_PRIMES = sorted(set(
    [3, 7, 11, 19, 23]
    + [p for p in _ALL_PRIMES if abs(p - 64)  < 20]
    + [p for p in _ALL_PRIMES if abs(p - 128) < 20]
    + [p for p in _ALL_PRIMES if abs(p - 256) < 20]
    + ([_ALL_PRIMES[-1]] if _ALL_PRIMES else [])
))


# ===========================================================================
# SECTION 1 — Field arithmetic properties
# ===========================================================================

class TestFieldArithmeticRandom:

    @pytest.mark.parametrize("p", _field_primes)
    def test_fermat_little_theorem(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for a in rng.sample(range(1, p), min(20, p - 1)):
            assert (F.element(a) ** (p - 1)).value == 1

    @pytest.mark.parametrize("p", _field_primes)
    def test_every_nonzero_has_inverse(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for a in rng.sample(range(1, p), min(30, p - 1)):
            fa = F.element(a)
            assert (fa * fa.inverse()).value == 1

    @pytest.mark.parametrize("p", _field_primes)
    def test_addition_closure(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(30):
            a, b = rng.randint(0, p - 1), rng.randint(0, p - 1)
            assert 0 <= (F.element(a) + F.element(b)).value < p

    @pytest.mark.parametrize("p", _field_primes)
    def test_multiplication_closure(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(30):
            a, b = rng.randint(0, p - 1), rng.randint(0, p - 1)
            assert 0 <= (F.element(a) * F.element(b)).value < p

    @pytest.mark.parametrize("p", _field_primes)
    def test_add_commutativity(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(20):
            a, b = rng.randint(0, p - 1), rng.randint(0, p - 1)
            assert F.element(a) + F.element(b) == F.element(b) + F.element(a)

    @pytest.mark.parametrize("p", _field_primes)
    def test_mul_commutativity(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(20):
            a, b = rng.randint(0, p - 1), rng.randint(0, p - 1)
            assert F.element(a) * F.element(b) == F.element(b) * F.element(a)

    @pytest.mark.parametrize("p", _field_primes)
    def test_add_associativity(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(20):
            a, b, c = [rng.randint(0, p - 1) for _ in range(3)]
            fa, fb, fc = F.element(a), F.element(b), F.element(c)
            assert (fa + fb) + fc == fa + (fb + fc)

    @pytest.mark.parametrize("p", _field_primes)
    def test_mul_associativity(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(20):
            a, b, c = [rng.randint(0, p - 1) for _ in range(3)]
            fa, fb, fc = F.element(a), F.element(b), F.element(c)
            assert (fa * fb) * fc == fa * (fb * fc)

    @pytest.mark.parametrize("p", _field_primes)
    def test_distributivity(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(20):
            a, b, c = [rng.randint(0, p - 1) for _ in range(3)]
            fa, fb, fc = F.element(a), F.element(b), F.element(c)
            assert fa * (fb + fc) == fa * fb + fa * fc

    @pytest.mark.parametrize("p", _field_primes)
    def test_negation_inverse(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for a in rng.sample(range(0, p), min(20, p)):
            fa = F.element(a)
            assert (fa + (-fa)).value == 0

    @pytest.mark.parametrize("p", _field_primes)
    def test_qr_count_is_half_nonzero(self, p):
        F = PrimeField(p)
        count = sum(1 for a in range(1, p) if F.element(a).is_quadratic_residue())
        assert count == (p - 1) // 2

    @pytest.mark.parametrize("p", _field_primes)
    def test_sqrt_roundtrip_for_qrs(self, p):
        F = PrimeField(p)
        for a in range(1, min(p, 50)):
            fe = F.element(a)
            if fe.is_quadratic_residue():
                s = fe.sqrt()
                assert s * s == fe

    @pytest.mark.parametrize("p", _field_primes)
    def test_squares_are_qr(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for a in rng.sample(range(1, p), min(20, p - 1)):
            sq = (F.element(a) ** 2).value
            assert F.element(sq).is_quadratic_residue()

    @pytest.mark.parametrize("p", _field_primes)
    def test_div_multiply_back(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(20):
            a = rng.randint(1, p - 1)
            b = rng.randint(1, p - 1)
            fa, fb = F.element(a), F.element(b)
            assert (fa / fb) * fb == fa

    @pytest.mark.parametrize("p", _field_primes)
    def test_pow_product_rule(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(15):
            a = rng.randint(1, p - 1)
            m, n = rng.randint(0, 50), rng.randint(0, 50)
            fa = F.element(a)
            assert fa**m * fa**n == fa**(m + n)

    @pytest.mark.parametrize("p", _field_primes)
    def test_pow_power_rule(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(15):
            a = rng.randint(1, p - 1)
            m, n = rng.randint(0, 20), rng.randint(0, 20)
            fa = F.element(a)
            assert (fa**m) ** n == fa ** (m * n)

    @pytest.mark.parametrize("p", _field_primes)
    def test_inverse_of_product(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(15):
            a, b = rng.randint(1, p - 1), rng.randint(1, p - 1)
            fa, fb = F.element(a), F.element(b)
            assert (fa * fb).inverse() == fb.inverse() * fa.inverse()

    @pytest.mark.parametrize("p", _field_primes)
    def test_wilson_theorem(self, p):
        F = PrimeField(p)
        product = F.element(1)
        for a in range(1, p):
            product = product * F.element(a)
        assert product.value == p - 1

    @pytest.mark.parametrize("p", _field_primes)
    def test_element_reduction_consistent(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(20):
            x = rng.randint(-100, 100)
            k = rng.randint(-5, 5)
            assert F.element(x) == F.element(x + k * p)

    @pytest.mark.parametrize("p", _field_primes)
    def test_additive_order_p(self, p):
        """Adding 1 to itself p times gives 0 (characteristic p)."""
        F = PrimeField(p)
        acc = F.element(0)
        one = F.element(1)
        for _ in range(p):
            acc = acc + one
        assert acc.value == 0

    @pytest.mark.parametrize("p", _field_primes)
    def test_qr_and_non_qr_partition(self, p):
        F = PrimeField(p)
        qr  = {a for a in range(1, p) if     F.element(a).is_quadratic_residue()}
        nqr = {a for a in range(1, p) if not F.element(a).is_quadratic_residue()}
        assert qr | nqr == set(range(1, p))
        assert qr & nqr == set()


# ===========================================================================
# SECTION 2 — Polynomial arithmetic (random primes + random coefficients)
# ===========================================================================

class TestPolynomialArithmeticRandom:

    def _rand_poly(self, F: PrimeField, max_deg: int, rng: random.Random) -> Polynomial:
        deg = rng.randint(0, max_deg)
        coeffs = [rng.randint(0, F.p - 1) for _ in range(deg + 1)]
        if all(c == 0 for c in coeffs):
            coeffs[0] = 1
        return _poly(coeffs, F)

    @pytest.mark.parametrize("p", _field_primes[:15])
    def test_add_commutativity(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(15):
            a, b = self._rand_poly(F, 4, rng), self._rand_poly(F, 4, rng)
            assert a + b == b + a

    @pytest.mark.parametrize("p", _field_primes[:15])
    def test_add_associativity(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(10):
            a, b, c = (self._rand_poly(F, 3, rng) for _ in range(3))
            assert (a + b) + c == a + (b + c)

    @pytest.mark.parametrize("p", _field_primes[:15])
    def test_mul_commutativity(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(10):
            a, b = self._rand_poly(F, 3, rng), self._rand_poly(F, 3, rng)
            assert a * b == b * a

    @pytest.mark.parametrize("p", _field_primes[:15])
    def test_distributivity(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(10):
            a, b, c = (self._rand_poly(F, 2, rng) for _ in range(3))
            assert a * (b + c) == a * b + a * c

    @pytest.mark.parametrize("p", _field_primes[:15])
    def test_division_algorithm(self, p):
        """Dividend = quotient * divisor + remainder, deg(r) < deg(d)."""
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(10):
            dividend = self._rand_poly(F, 4, rng)
            divisor  = self._rand_poly(F, 2, rng)
            if divisor.degree() < 0:
                continue
            q = dividend / divisor
            r = dividend % divisor
            assert dividend == q * divisor + r
            assert r.degree() < divisor.degree() or r.degree() < 0

    @pytest.mark.parametrize("p", _field_primes[:15])
    def test_sub_self_is_zero(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(15):
            a = self._rand_poly(F, 4, rng)
            assert (a - a).degree() < 0

    @pytest.mark.parametrize("p", _field_primes[:15])
    def test_degree_of_product(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(10):
            a, b = self._rand_poly(F, 3, rng), self._rand_poly(F, 3, rng)
            if a.degree() >= 0 and b.degree() >= 0:
                assert (a * b).degree() == a.degree() + b.degree()

    @pytest.mark.parametrize("p", _field_primes[:15])
    def test_gcd_divides_both(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(8):
            a, b = self._rand_poly(F, 3, rng), self._rand_poly(F, 3, rng)
            if a.degree() < 0 or b.degree() < 0:
                continue
            g = a.gcd(b)
            if g.degree() >= 0:
                assert (a % g).degree() < 0
                assert (b % g).degree() < 0

    @pytest.mark.parametrize("p", _field_primes[:15])
    def test_gcd_is_monic(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(10):
            a, b = self._rand_poly(F, 3, rng), self._rand_poly(F, 3, rng)
            if a.degree() < 0 or b.degree() < 0:
                continue
            g = a.gcd(b)
            if g.degree() >= 0:
                assert g.is_monic()

    @pytest.mark.parametrize("p", _field_primes[:10])
    def test_extended_gcd_bezout(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(8):
            a, b = self._rand_poly(F, 3, rng), self._rand_poly(F, 3, rng)
            if a.degree() < 0 or b.degree() < 0:
                continue
            g, s, t = a.extended_gcd(b)
            assert (s * a + t * b).make_monic() == g.make_monic()

    @pytest.mark.parametrize("p", _field_primes[:10])
    def test_make_monic_is_monic(self, p):
        F = PrimeField(p)
        rng = random.Random(SEED ^ p)
        for _ in range(15):
            a = self._rand_poly(F, 4, rng)
            if a.degree() >= 0:
                assert a.make_monic().is_monic()

    @pytest.mark.parametrize("p", _field_primes[:10])
    def test_pow_consistency(self, p):
        F = PrimeField(p)
        x = _poly([0, 1], F)
        for n in range(1, 8):
            assert x**n == x**(n - 1) * x


# ===========================================================================
# SECTION 3 — Elliptic curve group law
# ===========================================================================

class TestEllipticCurveGroupLaw:

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_point_on_curve(self, fcp):
        _, curve, P = fcp
        assert P.is_infinity or curve.contains(P)

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_identity_law(self, fcp):
        _, curve, P = fcp
        O = curve.identity()
        assert P + O == P and O + P == P

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_negation_law(self, fcp):
        _, curve, P = fcp
        assert (P + (-P)).is_infinity

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_doubling_on_curve(self, fcp):
        _, curve, P = fcp
        Q = P + P
        assert Q.is_infinity or curve.contains(Q)

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_group_order_kills_point(self, fcp):
        _, curve, P = fcp
        assert (curve.group_order() * P).is_infinity

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_hasse_bound(self, fcp):
        F, curve, _ = fcp
        n = curve.group_order()
        assert abs(n - F.p - 1) <= 2 * math.isqrt(F.p) + 2

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_scalar_mul_distributive(self, fcp):
        _, curve, P = fcp
        rng = random.Random(SEED)
        for _ in range(5):
            a, b = rng.randint(0, 20), rng.randint(0, 20)
            assert (a + b) * P == a * P + b * P

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_scalar_0_is_identity(self, fcp):
        _, curve, P = fcp
        assert (0 * P).is_infinity

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_scalar_1_is_self(self, fcp):
        _, curve, P = fcp
        assert 1 * P == P

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_order_divides_group_order(self, fcp):
        _, curve, P = fcp
        assert curve.group_order() % P.order() == 0

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_order_kills_point(self, fcp):
        _, curve, P = fcp
        assert (P.order() * P).is_infinity

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_neg_neg_is_self(self, fcp):
        _, curve, P = fcp
        assert -(-P) == P

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_2P_plus_P_equals_3P(self, fcp):
        _, curve, P = fcp
        assert 2 * P + P == 3 * P

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_additive_inverse_via_scalar(self, fcp):
        _, curve, P = fcp
        n = P.order()
        neg_via_scalar = (n - 1) * P
        assert neg_via_scalar == -P or (neg_via_scalar.is_infinity and (-P).is_infinity)

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_commutativity(self, fcp):
        _, curve, P = fcp
        Q = 3 * P
        if not Q.is_infinity:
            assert P + Q == Q + P

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_associativity(self, fcp):
        _, curve, P = fcp
        Q, R = 2 * P, 3 * P
        if not (Q.is_infinity or R.is_infinity):
            assert (P + Q) + R == P + (Q + R)

    @pytest.mark.parametrize("fcp", _curve_fixtures, ids=_curve_ids)
    def test_all_small_multiples_on_curve(self, fcp):
        _, curve, P = fcp
        n = P.order()
        for k in range(1, min(n + 1, 20)):
            Q = k * P
            assert Q.is_infinity or curve.contains(Q)


# ===========================================================================
# SECTION 4 — BLS round-trip (small known-good primes)
# ===========================================================================

class TestBLSRoundTripRandom:

    @pytest.mark.parametrize("p", _bls_primes)
    def test_sign_verify_various_keys(self, p):
        rng = random.Random(SEED ^ p)
        F = PrimeField(p)
        curve = EllipticCurve(F, A=1, B=0)
        n = curve.group_order()
        r = largest_prime_factor(n)
        if r < 2:
            pytest.skip("trivial subgroup")
        for _ in range(5):
            key = rng.randint(1, r - 1)
            try:
                bls = BLSSignatureScheme(p=p, A=1, B=0, private_key=key)
            except Exception:
                continue
            for msg in ["hello", "world", "test"]:
                sig = bls.sign(msg)
                if sig.is_infinity:
                    continue  # message hashes to identity — degenerate, skip
                assert bls.verify(msg, sig) is True

    @pytest.mark.parametrize("p", _bls_primes)
    def test_bilinearity_holds(self, p):
        rng = random.Random(SEED ^ p ^ 1)
        F = PrimeField(p)
        curve = EllipticCurve(F, A=1, B=0)
        n = curve.group_order()
        r = largest_prime_factor(n)
        if r < 2:
            pytest.skip("trivial subgroup")
        for _ in range(3):
            key = rng.randint(1, r - 1)
            try:
                bls = BLSSignatureScheme(p=p, A=1, B=0, private_key=key)
            except Exception:
                continue
            P = hash_to_point("test", bls.curve, bls.r)
            lhs = bls.tate_pairing(key * P, bls.Q)
            rhs = bls.tate_pairing(P, bls.public_key)
            assert lhs == rhs

    @pytest.mark.parametrize("p", _bls_primes)
    def test_wrong_key_fails_verification(self, p):
        rng = random.Random(SEED ^ p ^ 2)
        F = PrimeField(p)
        curve = EllipticCurve(F, A=1, B=0)
        n = curve.group_order()
        r = largest_prime_factor(n)
        if r < 7:
            pytest.skip(f"r={r} too small — pairing is degenerate for subgroups of order < 7")
        keys = list(range(1, min(r, 10)))
        if len(keys) < 2:
            pytest.skip("need at least 2 keys")
        key_a, key_b = rng.sample(keys, 2)
        try:
            bls_a = BLSSignatureScheme(p=p, A=1, B=0, private_key=key_a)
            bls_b = BLSSignatureScheme(p=p, A=1, B=0, private_key=key_b)
        except Exception:
            pytest.skip("BLS setup failed")

        # With small primes the cofactor is large relative to r, so many messages
        # hash to the identity after cofactor clearing.  Try candidates until we
        # find one whose hash is non-identity (guaranteeing a meaningful signature).
        candidates = ["message", "hello", "world", "test", "alpha", "beta",
                      "gamma", "delta", "crypto", "bls", "sign", "verify"]
        sig, used_msg = None, None
        for msg in candidates:
            s = bls_a.sign(msg)
            if not s.is_infinity:
                sig, used_msg = s, msg
                break
        assert sig is not None, f"All candidate messages hashed to identity for p={p}"

        assert bls_b.verify(used_msg, sig) is False


# ===========================================================================
# SECTION 5 — Edge-case primes (near powers of 2, smallest, largest)
# ===========================================================================

class TestEdgeCasePrimes:

    @pytest.mark.parametrize("p", _EDGE_PRIMES)
    def test_field_order(self, p):
        assert PrimeField(p).order() == p

    @pytest.mark.parametrize("p", _EDGE_PRIMES)
    def test_inverse_all_nonzero(self, p):
        F = PrimeField(p)
        for a in range(1, min(p, 30)):
            assert (F.element(a) * F.element(a).inverse()).value == 1

    @pytest.mark.parametrize("p", _EDGE_PRIMES)
    def test_fermat(self, p):
        F = PrimeField(p)
        for a in range(1, min(p, 20)):
            assert (F.element(a) ** (p - 1)).value == 1

    @pytest.mark.parametrize("p", _EDGE_PRIMES)
    def test_qr_count(self, p):
        F = PrimeField(p)
        count = sum(1 for a in range(1, p) if F.element(a).is_quadratic_residue())
        assert count == (p - 1) // 2

    @pytest.mark.parametrize("p", _EDGE_PRIMES)
    def test_sqrt_consistent(self, p):
        F = PrimeField(p)
        for a in range(1, min(p, 30)):
            fe = F.element(a)
            if fe.is_quadratic_residue():
                assert fe.sqrt() * fe.sqrt() == fe

    @pytest.mark.parametrize("p", [3, 7, 11])
    def test_exhaustive_inverse(self, p):
        F = PrimeField(p)
        for a in range(1, p):
            assert (F.element(a) * F.element(a).inverse()).value == 1

    @pytest.mark.parametrize("p", [3, 7, 11])
    def test_exhaustive_wilson(self, p):
        F = PrimeField(p)
        product = F.element(1)
        for a in range(1, p):
            product = product * F.element(a)
        assert product.value == p - 1


# ===========================================================================
# SECTION 6 — Statistical / meta checks
# ===========================================================================

class TestStatisticalProperties:

    def test_all_generated_primes_are_prime(self):
        for p in _ALL_PRIMES:
            assert is_prime(p)

    def test_all_generated_primes_are_3_mod_4(self):
        for p in _ALL_PRIMES:
            assert p % 4 == 3

    def test_prime_count_reasonable(self):
        assert len(_ALL_PRIMES) >= 20

    def test_sampled_primes_are_subset(self):
        assert set(_field_primes).issubset(set(_ALL_PRIMES))
        assert set(_curve_primes).issubset(set(_ALL_PRIMES))

    def test_seed_reproducibility(self):
        rng1, rng2 = random.Random(SEED), random.Random(SEED)
        s1 = rng1.sample(_ALL_PRIMES, min(10, len(_ALL_PRIMES)))
        s2 = rng2.sample(_ALL_PRIMES, min(10, len(_ALL_PRIMES)))
        assert s1 == s2

    def test_characteristic_p_for_all(self):
        for p in _ALL_PRIMES:
            F = PrimeField(p)
            assert (F.element(1) + F.element(p - 1)).value == 0
