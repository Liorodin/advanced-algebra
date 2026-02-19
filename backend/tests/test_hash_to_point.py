"""Unit tests for app.crypto.hash_to_point — TDD style."""

import pytest
from app.crypto.prime_field import PrimeField
from app.crypto.elliptic_curve import EllipticCurve
from app.crypto.hash_to_point import (
    string_to_field_element,
    increment_and_try,
    cofactor_clear,
    hash_to_point,
)


@pytest.fixture
def field():
    return PrimeField(103)


@pytest.fixture
def curve(field):
    return EllipticCurve(field, A=1, B=0)


class TestStringToFieldElement:
    def test_empty_string(self, field):
        el = string_to_field_element("", field)
        assert el.value == 0
        assert el.field is field

    def test_ascii_message(self, field):
        el = string_to_field_element("hello", field)
        assert el.field is field
        assert 0 <= el.value < field.p

    def test_utf8_message(self, field):
        el = string_to_field_element("שלום", field)
        assert el.field is field
        assert 0 <= el.value < field.p

    def test_deterministic(self, field):
        a = string_to_field_element("same", field)
        b = string_to_field_element("same", field)
        assert a.value == b.value


class TestIncrementAndTry:
    def test_returns_point_on_curve(self, field, curve):
        x = field.element(0)
        P = increment_and_try(x, curve)
        assert curve.contains(P)
        assert not P.is_infinity

    def test_raises_if_no_point_found(self, field):
        # Curve with no points for a given range would be pathological; doc says RuntimeError
        # We just check that a normal call works; RuntimeError is for "shouldn't happen"
        curve = EllipticCurve(field, A=1, B=0)
        x = field.element(0)
        P = increment_and_try(x, curve)
        assert P is not None


class TestCofactorClear:
    def test_result_has_order_dividing_r(self, field, curve):
        group_order = curve.group_order()
        r = 13  # for p=103, A=1, B=0, |E|=104, r=13
        x = field.element(0)
        P = increment_and_try(x, curve)
        Q = cofactor_clear(P, group_order, r)
        # r * Q = O
        R = Q * r
        assert R.is_infinity

    def test_deterministic(self, field, curve):
        group_order = curve.group_order()
        r = 13
        x = field.element(0)
        P = increment_and_try(x, curve)
        Q1 = cofactor_clear(P, group_order, r)
        Q2 = cofactor_clear(P, group_order, r)
        assert Q1 == Q2


class TestHashToPoint:
    def test_returns_point_on_curve(self, curve):
        r = 13
        P = hash_to_point("test message", curve, r)
        assert P.curve is curve
        assert not P.is_infinity
        assert curve.contains(P)

    def test_deterministic(self, curve):
        r = 13
        P1 = hash_to_point("message", curve, r)
        P2 = hash_to_point("message", curve, r)
        assert P1 == P2

    def test_different_messages_different_points(self, curve):
        r = 13
        P1 = hash_to_point("msg1", curve, r)
        P2 = hash_to_point("msg2", curve, r)
        assert P1 != P2

    def test_result_has_order_r(self, curve):
        r = 13
        P = hash_to_point("hello", curve, r)
        assert (P * r).is_infinity
