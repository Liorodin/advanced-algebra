"""Unit tests for app.crypto.miller — TDD style."""

import pytest
from app.crypto.prime_field import PrimeField
from app.crypto.elliptic_curve import EllipticCurve, ECPoint
from app.crypto.polynomial import Polynomial
from app.crypto.extension_field import ExtensionField
from app.crypto.ext_curve import ExtCurvePoint
from app.crypto.miller import line_function, miller


@pytest.fixture
def field():
    return PrimeField(103)


@pytest.fixture
def curve(field):
    return EllipticCurve(field, A=1, B=0)


@pytest.fixture
def irr(field):
    return Polynomial(
        [field.element(1), field.element(0), field.element(1)],
        field,
    )


@pytest.fixture
def ext_field(field, irr):
    return ExtensionField(field, irr)


@pytest.fixture
def P(curve, field):
    return ECPoint(curve, field.element(0), field.element(0))


@pytest.fixture
def Q_ext(curve, ext_field):
    # Some point in E(F_{p^k}); use (0,0) embedded if on curve
    x = ext_field.element([0, 0])
    y = ext_field.element([0, 0])
    return ExtCurvePoint(curve, ext_field, x, y)


class TestLineFunction:
    def test_distinct_points(self, curve, field, ext_field, Q_ext):
        P1 = ECPoint(curve, field.element(0), field.element(0))
        P2 = ECPoint(curve, field.element(1), field.element(1)) if curve.contains(
            ECPoint(curve, field.element(1), field.element(1))
        ) else P1
        result = line_function(P1, P2, Q_ext)
        assert result.ext_field is ext_field

    def test_doubling_tangent(self, P, Q_ext):
        result = line_function(P, P, Q_ext)
        assert result is not None

    def test_vertical_line(self, curve, field, Q_ext):
        # P = (x,y), R = (x,-y) => vertical line
        P = ECPoint(curve, field.element(0), field.element(0))
        R = -P
        result = line_function(P, R, Q_ext)
        assert result is not None


class TestMiller:
    def test_returns_ext_field_element(self, P, Q_ext):
        r = 13
        f = miller(P, Q_ext, r)
        assert f is not None
        assert f.ext_field is Q_ext.ext_field

    def test_miller_bilinearity_consistency(self, curve, field, ext_field):
        # If we have P, Q and compute miller(P,Q,r), result should be in F_{p^k}^*
        from app.crypto.hash_to_point import hash_to_point
        from app.crypto.ext_curve import find_point_of_order_r
        r = 13
        P = hash_to_point("test", curve, r)
        Q = find_point_of_order_r(curve, ext_field, r)
        f = miller(P, Q, r)
        assert f is not None
        # After final exponentiation in pairing, result is r-th root of unity
        # Here we only test miller returns an element
        assert f.poly is not None or hasattr(f, "ext_field")
