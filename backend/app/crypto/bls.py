"""BLS Signature Scheme using the Reduced Tate Pairing.

Orchestrates all cryptographic components:
- Key generation: private key a, public key aQ
- Signing: sig = a * H(m)
- Verification: e_r(sig, Q) == e_r(H(m), aQ)

The security relies on the bilinearity of the pairing:
    e_r(aP, Q) = e_r(P, Q)^a = e_r(P, aQ)
"""

from __future__ import annotations
from typing import Any

from app.crypto.prime_field import PrimeField
from app.crypto.elliptic_curve import EllipticCurve, ECPoint
from app.crypto.extension_field import ExtensionField, ExtFieldElement
from app.crypto.ext_curve import ExtCurvePoint, find_point_of_order_r
from app.crypto.hash_to_point import hash_to_point
from app.crypto.miller import miller
from app.crypto.utils import largest_prime_factor


class BLSSignatureScheme:
    """BLS Signature Scheme orchestrator.

    Sets up all the algebraic structures needed for BLS signatures:
    - Prime field F_p
    - Elliptic curve E(F_p)
    - Group order |G| and largest prime factor r
    - Embedding degree k and extension field F_{p^k}
    - Public point Q in E(F_{p^k})

    Attributes:
        field: PrimeField F_p.
        curve: EllipticCurve E(F_p).
        private_key: Integer secret key a.
        group_order: |E(F_p)|.
        r: Largest prime factor of group_order.
        cofactor: group_order / r.
        k: Embedding degree.
        ext_field: ExtensionField F_{p^k}.
        Q: ExtCurvePoint of order r in E(F_{p^k}).
        public_key: aQ (ExtCurvePoint).
    """

    def __init__(self, p: int, A: int, B: int, private_key: int) -> None:
        """Initialize the BLS signature scheme.

        Setup pipeline:
        1. Create PrimeField(p)
        2. Create EllipticCurve(field, A, B)
        3. Compute group_order = |E(F_p)|
        4. Find r = largest_prime_factor(group_order)
        5. Compute cofactor = group_order / r
        6. Find embedding degree k
        7. Find irreducible polynomial of degree k
        8. Create ExtensionField
        9. Find point Q of order r in E(F_{p^k})
        10. Compute public_key = private_key * Q

        Args:
            p: Prime field characteristic.
            A: Curve parameter A.
            B: Curve parameter B.
            private_key: Secret key integer a.

        Raises:
            ValueError: If parameters are invalid.
        """
        # Step 1: Create prime field
        self.field = PrimeField(p)
        
        # Step 2: Create elliptic curve
        self.curve = EllipticCurve(self.field, A, B)
        
        # Step 3: Compute group order
        self.group_order = self.curve.group_order()
        
        # Step 4: Find largest prime factor r
        self.r = largest_prime_factor(self.group_order)
        
        # Step 5: Compute cofactor
        self.cofactor = self.group_order // self.r
        
        # Step 6: Find embedding degree k
        self.k = ExtensionField.find_embedding_degree(p, self.r)
        
        # Step 7: Find irreducible polynomial
        irr_poly = ExtensionField.find_irreducible(self.field, self.k)
        
        # Step 8: Create extension field
        self.ext_field = ExtensionField(self.field, irr_poly)
        
        # Step 9: Find point Q of order r in E(F_{p^k})
        self.Q = find_point_of_order_r(self.curve, self.ext_field, self.r)
        
        # Step 10: Store private key and compute public key
        self.private_key = private_key
        self.public_key = private_key * self.Q

    def sign(self, message: str) -> ECPoint:
        """Sign a message: compute sig = a * H(m).

        Args:
            message: The message string to sign.

        Returns:
            ECPoint representing the signature a * H(m).
        """
        H_m = hash_to_point(message, self.curve, self.r)
        signature = self.private_key * H_m
        return signature

    def tate_pairing(self, P: ECPoint, Q: ExtCurvePoint) -> ExtFieldElement:
        """Compute the reduced Tate pairing e_r(P, Q).

        e_r(P, Q) = f_{r,P}(Q) ^ ((p^k - 1) / r)

        The final exponentiation ensures the result is in the r-th roots
        of unity in F_{p^k}^*, making the pairing well-defined.

        Args:
            P: Point in E(F_p) of order r.
            Q: Point in E(F_{p^k}) of order r.

        Returns:
            ExtFieldElement — the pairing value in F_{p^k}^*.
        """
        # Compute Miller function
        f = miller(P, Q, self.r)
        
        # Final exponentiation: raise to (p^k - 1) / r
        p = self.field.p
        pk = p ** self.k
        exponent = (pk - 1) // self.r
        
        e_r = f ** exponent
        return e_r

    def verify(self, message: str, signature: ECPoint) -> bool:
        """Verify a BLS signature.

        Checks: e_r(sig, Q) == e_r(H(m), aQ)

        By bilinearity:
        - LHS = e_r(a*H(m), Q) = e_r(H(m), Q)^a
        - RHS = e_r(H(m), a*Q) = e_r(H(m), Q)^a
        So they should be equal if the signature is valid.

        Args:
            message: The original message.
            signature: The alleged signature (ECPoint).

        Returns:
            True if the signature is valid.
        """
        # Compute H(m)
        H_m = hash_to_point(message, self.curve, self.r)
        
        # Compute LHS: e_r(sig, Q)
        lhs = self.tate_pairing(signature, self.Q)
        
        # Compute RHS: e_r(H(m), aQ)
        rhs = self.tate_pairing(H_m, self.public_key)
        
        # Compare
        return lhs == rhs

    def get_steps(self, message: str) -> dict[str, Any]:
        """Return all intermediate computation steps for display.

        This is used by the frontend to show the step-by-step computation.

        Args:
            message: The message being signed.

        Returns:
            Dictionary containing all intermediate values:
            - group_order, r, cofactor, embedding_degree
            - irreducible_poly (string representation)
            - hash_point (x, y of H(m))
            - signature (x, y of sig)
            - Q (x, y as extension field element strings)
            - pairing_lhs, pairing_rhs (string representations)
            - verified (bool)
        """
        # Sign the message
        H_m = hash_to_point(message, self.curve, self.r)
        signature = self.sign(message)
        
        # Compute pairings
        pairing_lhs = self.tate_pairing(signature, self.Q)
        pairing_rhs = self.tate_pairing(H_m, self.public_key)
        
        # Verify
        verified = (pairing_lhs == pairing_rhs)
        
        # Collect all steps
        return {
            "group_order": self.group_order,
            "r": self.r,
            "cofactor": self.cofactor,
            "embedding_degree": self.k,
            "irreducible_poly": str(self.ext_field.modulus),
            "hash_point": {
                "x": str(H_m.x.value) if not H_m.is_infinity else None,
                "y": str(H_m.y.value) if not H_m.is_infinity else None,
            },
            "signature": {
                "x": str(signature.x.value) if not signature.is_infinity else None,
                "y": str(signature.y.value) if not signature.is_infinity else None,
            },
            "Q": {
                "x": str(self.Q.x) if not self.Q.is_infinity else None,
                "y": str(self.Q.y) if not self.Q.is_infinity else None,
            },
            "public_key": {
                "x": str(self.public_key.x) if not self.public_key.is_infinity else None,
                "y": str(self.public_key.y) if not self.public_key.is_infinity else None,
            },
            "pairing_lhs": str(pairing_lhs),
            "pairing_rhs": str(pairing_rhs),
            "verified": verified,
            "display_message": f'{"✓" if verified else "✗"} Message was {"verified" if verified else "NOT verified"}',
        }
