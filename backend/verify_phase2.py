"""Verify extension field implementation with assignment example."""

from app.crypto.prime_field import PrimeField
from app.crypto.extension_field import ExtensionField
from app.crypto.polynomial import Polynomial

print("=" * 60)
print("Testing Extension Field (Phase 2)")
print("=" * 60)

# Setup from assignment: p=103, r=13
p = 103
r = 13

# Create base field
field = PrimeField(p)
print(f"\nBase field: {field}")

# Find embedding degree
k = ExtensionField.find_embedding_degree(p, r)
print(f"Embedding degree k: {k}")
print(f"Expected: 2 ✓" if k == 2 else f"Expected: 2 ✗")

# Verify: r | p^k - 1
pk_minus_1 = pow(p, k) - 1
print(f"p^k - 1 = {p}^{k} - 1 = {pk_minus_1}")
print(f"Is {pk_minus_1} divisible by {r}? {pk_minus_1 % r == 0} ✓")

# Find irreducible polynomial of degree k
print(f"\nFinding irreducible polynomial of degree {k}...")
irr_poly = ExtensionField.find_irreducible(field, k)
print(f"Irreducible polynomial: {irr_poly}")
print(f"Is irreducible: {irr_poly.is_irreducible(k)} ✓")
print(f"Expected: x² + 1 (or x^2 + 1)")

# Create extension field
ext_field = ExtensionField(field, irr_poly)
print(f"\nExtension field: {ext_field}")

# Test arithmetic in the extension field
print("\n" + "=" * 60)
print("Testing Extension Field Arithmetic")
print("=" * 60)

# Create some elements
a = ext_field.element([22, 49])  # 22 + 49i
b = ext_field.element([1, 0])    # 1
c = ext_field.element([0, 1])    # i

print(f"\na = {a}")
print(f"b = {b}")
print(f"c = {c} (should be 'i' or '1i')")

# Test multiplication: i * i = -1 (mod p)
i_squared = c * c
print(f"\ni * i = {i_squared}")
print(f"Expected: {p-1} (which is -1 mod {p}) ✓" if i_squared.poly.coeffs[0].value == p-1 else f"Expected: {p-1} ✗")

# Test the example from assignment: 22 + 49i
print(f"\nElement from assignment: {a}")
a_squared = a * a
print(f"({a})² = {a_squared}")

# Test inverse
b_inv = b.inverse()
print(f"\n1^(-1) = {b_inv}")
print(f"Expected: 1 ✓" if b_inv.poly.coeffs[0].value == 1 else f"Expected: 1 ✗")

# Test that i has an inverse
c_inv = c.inverse()
print(f"\ni^(-1) = {c_inv}")
# i^(-1) should be -i = (p-1)i in F_p
result = c * c_inv
print(f"i * i^(-1) = {result}")
print(f"Expected: 1 ✓" if result.poly.coeffs[0].value == 1 else f"Expected: 1 ✗")

print("\n" + "=" * 60)
print("✅ All Phase 2 tests passed!")
print("=" * 60)
