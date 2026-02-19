"""Unit tests for app.crypto.bls (BLSSignatureScheme) — TDD style."""

import pytest
from app.crypto.elliptic_curve import ECPoint
from app.crypto.bls import BLSSignatureScheme


@pytest.fixture
def valid_params():
    return {"p": 103, "A": 1, "B": 0, "private_key": 7}


class TestBLSSignatureSchemeInit:
    def test_init_succeeds_with_valid_params(self, valid_params):
        scheme = BLSSignatureScheme(
            p=valid_params["p"],
            A=valid_params["A"],
            B=valid_params["B"],
            private_key=valid_params["private_key"],
        )
        assert scheme.private_key == 7
        assert scheme.field is not None
        assert scheme.curve is not None
        assert scheme.r >= 2
        assert scheme.k >= 1

    def test_init_raises_on_invalid_curve(self):
        with pytest.raises(ValueError):
            BLSSignatureScheme(p=103, A=0, B=0, private_key=1)


class TestBLSSignatureSchemeSign:
    def test_sign_returns_ec_point(self, valid_params):
        scheme = BLSSignatureScheme(**valid_params)
        sig = scheme.sign("hello")
        assert isinstance(sig, ECPoint)
        assert sig.curve is scheme.curve

    def test_sign_deterministic(self, valid_params):
        scheme = BLSSignatureScheme(**valid_params)
        s1 = scheme.sign("msg")
        s2 = scheme.sign("msg")
        assert s1 == s2


class TestBLSSignatureSchemeTatePairing:
    def test_tate_pairing_returns_ext_field_element(self, valid_params):
        scheme = BLSSignatureScheme(**valid_params)
        msg = "test"
        Hm = scheme.sign(msg)  # Actually we need H(m) and Q; get_steps builds them
        # Use scheme's internal Q
        from app.crypto.ext_curve import ExtCurvePoint
        assert hasattr(scheme, "Q")
        pairing_val = scheme.tate_pairing(Hm, scheme.Q)
        assert pairing_val is not None
        assert hasattr(pairing_val, "ext_field") or hasattr(pairing_val, "poly")


class TestBLSSignatureSchemeVerify:
    def test_verify_valid_signature_returns_true(self, valid_params):
        scheme = BLSSignatureScheme(**valid_params)
        msg = "message"
        sig = scheme.sign(msg)
        assert scheme.verify(msg, sig) is True

    def test_verify_tampered_message_returns_false(self, valid_params):
        scheme = BLSSignatureScheme(**valid_params)
        sig = scheme.sign("original")
        assert scheme.verify("tampered", sig) is False

    def test_verify_wrong_signature_returns_false(self, valid_params):
        scheme = BLSSignatureScheme(**valid_params)
        msg = "same"
        sig_correct = scheme.sign(msg)
        # Forge a different point (e.g. double the correct sig)
        sig_wrong = sig_correct + sig_correct
        assert scheme.verify(msg, sig_wrong) is False


class TestBLSSignatureSchemeGetSteps:
    def test_get_steps_returns_dict_with_required_keys(self, valid_params):
        scheme = BLSSignatureScheme(**valid_params)
        steps = scheme.get_steps("hello")
        required = [
            "group_order", "r", "cofactor", "embedding_degree",
            "irreducible_poly", "hash_point", "signature", "Q",
            "pairing_lhs", "pairing_rhs", "verified", "display_message",
        ]
        for key in required:
            assert key in steps, f"Missing key: {key}"

    def test_get_steps_verified_true_for_valid_flow(self, valid_params):
        scheme = BLSSignatureScheme(**valid_params)
        steps = scheme.get_steps("test message")
        assert steps["verified"] is True

    def test_get_steps_hash_point_and_signature_are_point_like(self, valid_params):
        scheme = BLSSignatureScheme(**valid_params)
        steps = scheme.get_steps("msg")
        assert "x" in steps["hash_point"] and "y" in steps["hash_point"]
        assert "x" in steps["signature"] and "y" in steps["signature"]
