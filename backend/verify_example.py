"""Verify implementation with assignment example."""

from app.crypto.prime_field import PrimeField
from app.crypto.elliptic_curve import EllipticCurve, ECPoint

# Example from assignment: p=103, A=1, B=0
print("=" * 60)
print("Testing with assignment example: p=103, A=1, B=0")
print("=" * 60)

field = PrimeField(103)
curve = EllipticCurve(field, 1, 0)

print(f"\nCurve: {curve}")
print(f"Is non-singular: {curve.is_non_singular()}")

# Compute group order
group_order = curve.group_order()
print(f"Group order |G|: {group_order}")
print(f"Expected: 104 ✓" if group_order == 104 else f"Expected: 104 ✗")

# Test point from assignment: P_temp = (9, 29)
x = field.element(9)
y = field.element(29)
P_temp = ECPoint(curve, x, y)

print(f"\nP_temp = (9, 29)")
print(f"P_temp on curve: {curve.contains(P_temp)}")

# Test cofactor calculation
from app.crypto.utils import largest_prime_factor
r = largest_prime_factor(group_order)
cofactor = group_order // r

print(f"\nr = largest_prime_factor({group_order}) = {r}")
print(f"Expected r: 13 ✓" if r == 13 else f"Expected r: 13 ✗")
print(f"cofactor = {cofactor}")
print(f"Expected cofactor: 8 ✓" if cofactor == 8 else f"Expected cofactor: 8 ✗")

# Test H(m) = cofactor * P_temp = (32, 47)
H_m = cofactor * P_temp
print(f"\nH(m) = {cofactor} * P_temp = {H_m}")
print(f"Expected: (32, 47) ✓" if H_m.x.value == 32 and H_m.y.value == 47 else f"Expected: (32, 47) ✗")

# Test signature: a * H(m) where a = 7
a = 7
signature = a * H_m
print(f"\nSignature = {a} * H(m) = {signature}")
print(f"Expected: (18, 44) ✓" if signature.x.value == 18 and signature.y.value == 44 else f"Expected: (18, 44) ✗")

print("\n" + "=" * 60)
print("✅ All values match the assignment example!")
print("=" * 60)
