"""Unit tests for app.crypto.elliptic_curve — TDD style."""

import pytest
from app.crypto.prime_field import PrimeField
from app.crypto.elliptic_curve import EllipticCurve, ECPoint


@pytest.fixture
def field():
    return PrimeField(103)


@pytest.fixture
def curve(field):
    return EllipticCurve(field, A=1, B=0)


class TestEllipticCurve:
    def test_init_stores_params(self, curve, field):
        assert curve.field is field
        assert curve.A.value == 1
        assert curve.B.value == 0

    def test_init_rejects_singular_curve(self, field):
        # 4A^3 + 27B^2 = 0 for A = 0, B = 0 (or specific combos)
        with pytest.raises(ValueError):
            EllipticCurve(field, A=0, B=0)

    def test_is_non_singular(self, curve):
        assert curve.is_non_singular() is True

    def test_group_order_example(self, curve):
        # doc: For p=103, A=1, B=0: |E(F_103)| = 104
        assert curve.group_order() == 104

    def test_contains_point_on_curve(self, curve, field):
        # (1, 1): 1^2 = 1, 1^3 + 1 = 2, so 1 != 2. (2,?) 2^3+2=10, need y^2=10. Try (0,0): 0=0+0, so (0,0) on curve
        pt = ECPoint(curve, field.element(0), field.element(0))
        assert curve.contains(pt) is True

    def test_identity(self, curve):
        O = curve.identity()
        assert O.is_infinity is True
        assert O.x is None and O.y is None

    def test_repr(self, curve):
        assert repr(curve) is not None


class TestECPoint:
    def test_init_infinity(self, curve):
        O = ECPoint(curve, None, None, is_infinity=True)
        assert O.is_infinity

    def test_init_affine(self, curve, field):
        P = ECPoint(curve, field.element(0), field.element(0))
        assert not P.is_infinity
        assert P.x.value == 0 and P.y.value == 0

    def test_add_identity(self, curve, field):
        O = curve.identity()
        P = ECPoint(curve, field.element(0), field.element(0))
        assert (P + O).x.value == P.x.value and (P + O).y.value == P.y.value
        assert (O + P).x.value == P.x.value

    def test_neg(self, curve, field):
        P = ECPoint(curve, field.element(0), field.element(0))
        Q = -P
        assert Q.x.value == P.x.value
        assert Q.y.value == (-P.y).value

    def test_doubling(self, curve, field):
        P = ECPoint(curve, field.element(0), field.element(0))
        R = P + P
        assert curve.contains(R)

    def test_scalar_mul_zero(self, curve, field):
        P = ECPoint(curve, field.element(0), field.element(0))
        assert (0 * P).is_infinity

    def test_scalar_mul_one(self, curve, field):
        P = ECPoint(curve, field.element(0), field.element(0))
        assert (1 * P) == P

    def test_rmul(self, curve, field):
        P = ECPoint(curve, field.element(0), field.element(0))
        Q = 2 * P
        assert curve.contains(Q)

    def test_eq(self, curve, field):
        P = ECPoint(curve, field.element(0), field.element(0))
        Q = ECPoint(curve, field.element(0), field.element(0))
        assert P == Q

    def test_order_divides_group_order(self, curve, field):
        P = ECPoint(curve, field.element(0), field.element(0))
        n = curve.group_order()
        ord_p = P.order()
        assert n % ord_p == 0

    def test_repr(self, curve, field):
        P = ECPoint(curve, field.element(0), field.element(0))
        r = repr(P)
        assert "0" in r or "O" in r or "infinity" in r.lower()
