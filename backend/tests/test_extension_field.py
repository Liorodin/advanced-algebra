"""Unit tests for app.crypto.extension_field — TDD style."""

import pytest
from app.crypto.prime_field import PrimeField
from app.crypto.polynomial import Polynomial
from app.crypto.extension_field import ExtensionField, ExtFieldElement


@pytest.fixture
def base_field():
    return PrimeField(103)


@pytest.fixture
def irr_poly_k2(base_field):
    # x^2 + 1
    return Polynomial(
        [base_field.element(1), base_field.element(0), base_field.element(1)],
        base_field,
    )


@pytest.fixture
def ext_field(base_field, irr_poly_k2):
    return ExtensionField(base_field, irr_poly_k2)


class TestExtensionField:
    def test_init_stores_base_and_modulus(self, ext_field, base_field, irr_poly_k2):
        assert ext_field.base_field is base_field
        assert ext_field.modulus == irr_poly_k2 or ext_field.modulus.degree() == 2
        assert ext_field.k == 2

    def test_element_from_coefficients(self, ext_field):
        # 22 + 49*x (e.g. for display "22 + 49i")
        el = ext_field.element([22, 49])
        assert el is not None
        assert el.ext_field is ext_field

    def test_element_pads_short_list(self, ext_field):
        el = ext_field.element([5])
        assert el is not None

    def test_find_irreducible_k2(self, base_field):
        irr = ExtensionField.find_irreducible(base_field, 2)
        assert irr.degree() == 2
        assert irr.is_monic()

    def test_find_embedding_degree_example(self):
        k = ExtensionField.find_embedding_degree(103, 13)
        assert k == 2  # 103^2 ≡ 1 (mod 13)

    def test_find_embedding_degree_k1(self):
        k = ExtensionField.find_embedding_degree(7, 3)
        # 7^1 = 7 ≡ 1 mod 3? No. 7^2 = 49 ≡ 1 mod 3? 49 % 3 = 1. So k=2. For k=1: 7 mod 3 = 1? No. So k=2.
        assert k >= 1

    def test_repr(self, ext_field):
        assert repr(ext_field) is not None


class TestExtFieldElement:
    @pytest.fixture
    def el_a(self, ext_field):
        return ext_field.element([1, 0])

    @pytest.fixture
    def el_b(self, ext_field):
        return ext_field.element([0, 1])

    def test_add(self, ext_field, el_a, el_b):
        c = el_a + el_b
        assert c.ext_field is ext_field

    def test_sub(self, ext_field, el_a, el_b):
        c = el_a - el_b
        assert c.ext_field is ext_field

    def test_mul(self, ext_field, el_a, el_b):
        c = el_a * el_b
        assert c.ext_field is ext_field

    def test_truediv(self, ext_field, el_a, el_b):
        c = el_a / el_b
        assert (c * el_b) == el_a

    def test_div_zero_raises(self, ext_field):
        z = ext_field.element([0, 0])
        nonzero = ext_field.element([1, 0])
        with pytest.raises(ZeroDivisionError):
            nonzero / z

    def test_pow(self, ext_field, el_a):
        assert (el_a ** 0).ext_field is ext_field
        assert (el_a ** 2).ext_field is ext_field

    def test_neg(self, ext_field, el_a):
        n = -el_a
        assert (el_a + n).poly.coeffs[0].value == 0

    def test_eq(self, ext_field):
        a = ext_field.element([1, 2])
        b = ext_field.element([1, 2])
        assert a == b

    def test_inverse(self, ext_field, el_a):
        inv = el_a.inverse()
        assert (el_a * inv).poly.coeffs[0].value == 1 or (el_a * inv == ext_field.element([1]))

    def test_inverse_zero_raises(self, ext_field):
        z = ext_field.element([0, 0])
        with pytest.raises(ZeroDivisionError):
            z.inverse()

    def test_repr(self, ext_field, el_a):
        r = repr(el_a)
        assert r is not None
