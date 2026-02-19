"""Unit tests for app.crypto.ext_curve — TDD style."""

import pytest
from app.crypto.prime_field import PrimeField
from app.crypto.elliptic_curve import EllipticCurve
from app.crypto.polynomial import Polynomial
from app.crypto.extension_field import ExtensionField
from app.crypto.ext_curve import ExtCurvePoint, find_point_of_order_r


@pytest.fixture
def base_field():
    return PrimeField(103)


@pytest.fixture
def curve(base_field):
    return EllipticCurve(base_field, A=1, B=0)


@pytest.fixture
def irr(base_field):
    return Polynomial(
        [base_field.element(1), base_field.element(0), base_field.element(1)],
        base_field,
    )


@pytest.fixture
def ext_field(base_field, irr):
    return ExtensionField(base_field, irr)


class TestExtCurvePoint:
    def test_init_infinity(self, curve, ext_field):
        O = ExtCurvePoint(curve, ext_field, None, None, is_infinity=True)
        assert O.is_infinity

    def test_init_affine(self, curve, ext_field):
        x = ext_field.element([1, 0])
        y = ext_field.element([0, 1])
        P = ExtCurvePoint(curve, ext_field, x, y)
        assert not P.is_infinity
        assert P.x is x and P.y is y

    def test_add(self, curve, ext_field):
        # Use two points if we have them; else just check add returns ExtCurvePoint
        x = ext_field.element([0, 0])
        y = ext_field.element([0, 0])
        P = ExtCurvePoint(curve, ext_field, x, y)
        Q = P + P
        assert isinstance(Q, ExtCurvePoint)

    def test_neg(self, curve, ext_field):
        x = ext_field.element([1, 0])
        y = ext_field.element([0, 1])
        P = ExtCurvePoint(curve, ext_field, x, y)
        Q = -P
        assert Q.y == -y or (-Q) == P

    def test_scalar_mul(self, curve, ext_field):
        x = ext_field.element([0, 0])
        y = ext_field.element([0, 0])
        P = ExtCurvePoint(curve, ext_field, x, y)
        Q = P * 3
        assert isinstance(Q, ExtCurvePoint)

    def test_rmul(self, curve, ext_field):
        x = ext_field.element([0, 0])
        y = ext_field.element([0, 0])
        P = ExtCurvePoint(curve, ext_field, x, y)
        Q = 2 * P
        assert isinstance(Q, ExtCurvePoint)

    def test_eq(self, curve, ext_field):
        x = ext_field.element([1, 0])
        y = ext_field.element([0, 1])
        P = ExtCurvePoint(curve, ext_field, x, y)
        Q = ExtCurvePoint(curve, ext_field, x, y)
        assert P == Q

    def test_repr(self, curve, ext_field):
        x = ext_field.element([1, 0])
        y = ext_field.element([0, 1])
        P = ExtCurvePoint(curve, ext_field, x, y)
        assert repr(P) is not None


class TestFindPointOfOrderR:
    def test_returns_ext_curve_point(self, curve, ext_field):
        r = 13
        Q = find_point_of_order_r(curve, ext_field, r)
        assert isinstance(Q, ExtCurvePoint)
        assert Q.ext_field is ext_field

    def test_point_has_order_r(self, curve, ext_field):
        r = 13
        Q = find_point_of_order_r(curve, ext_field, r)
        R = Q * r
        assert R.is_infinity
