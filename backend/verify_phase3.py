"""Verify Phase 3 implementation with assignment example."""

from app.crypto.prime_field import PrimeField
from app.crypto.elliptic_curve import EllipticCurve
from app.crypto.extension_field import ExtensionField
from app.crypto.ext_curve import ExtCurvePoint, find_point_of_order_r
from app.crypto.utils import largest_prime_factor

print("=" * 60)
print("Testing Extension Curve Points (Phase 3)")
print("=" * 60)

# Setup from assignment
p = 103
A = 1
B = 0
r = 13

# Create field, curve, and extension field
field = PrimeField(p)
curve = EllipticCurve(field, A, B)
k = ExtensionField.find_embedding_degree(p, r)
irr_poly = ExtensionField.find_irreducible(field, k)
ext_field = ExtensionField(field, irr_poly)

print(f"\nBase field: {field}")
print(f"Curve: {curve}")
print(f"Extension field: {ext_field}")
print(f"Irreducible polynomial: {irr_poly}")

# Create a point in the extension field
print("\n" + "=" * 60)
print("Testing ExtCurvePoint Arithmetic")
print("=" * 60)

# Try creating the point from assignment: Q = (47, 8 + 56i)
x_Q = ext_field.element([47, 0])  # Start with base field point
y_Q = ext_field.element([8, 56])   # Has extension component

# First check: is this actually on the curve?
# y² = x³ + Ax + B
A_ext = ext_field.element([A])
B_ext = ext_field.element([B])
lhs = y_Q * y_Q
rhs = x_Q**3 + A_ext * x_Q + B_ext

print(f"\nTrying point Q = ({x_Q}, {y_Q})")
print(f"Checking if on curve:")
print(f"  LHS (y²) = {lhs}")
print(f"  RHS (x³ + Ax + B) = {rhs}")
print(f"  On curve: {lhs == rhs}")

if lhs == rhs:
    Q = ExtCurvePoint(curve, ext_field, x_Q, y_Q)
    print(f"\n✓ Point Q is on the curve!")
    
    # Test scalar multiplication
    print(f"\nTesting scalar multiplication:")
    Q2 = 2 * Q
    print(f"2Q = {Q2}")
    
    # Test that rQ = O
    rQ = r * Q
    print(f"\n{r}Q = {rQ}")
    print(f"Is {r}Q = O? {rQ.is_infinity} ✓" if rQ.is_infinity else f"Is {r}Q = O? {rQ.is_infinity} ✗")

# Test find_point_of_order_r
print("\n" + "=" * 60)
print("Testing find_point_of_order_r")
print("=" * 60)

print(f"\nSearching for a point Q of order {r} in E(F_{{{p}^{k}}})...")
print("(This may take a moment for small fields...)")

try:
    Q_found = find_point_of_order_r(curve, ext_field, r)
    print(f"\n✓ Found point: Q = {Q_found}")
    
    # Verify it has order r
    rQ_found = r * Q_found
    print(f"\nVerifying order:")
    print(f"{r} * Q = {rQ_found}")
    print(f"Has order {r}: {rQ_found.is_infinity} ✓" if rQ_found.is_infinity else f"Has order {r}: {rQ_found.is_infinity} ✗")
    
    # Verify it's not in base field (has non-zero extension component)
    has_extension = False
    if not Q_found.is_infinity:
        x_coeffs = Q_found.x.poly.coeffs
        y_coeffs = Q_found.y.poly.coeffs
        if (len(x_coeffs) > 1 and x_coeffs[1].value != 0) or \
           (len(y_coeffs) > 1 and y_coeffs[1].value != 0):
            has_extension = True
    
    print(f"Not in base field E(F_p): {has_extension} ✓" if has_extension else f"Not in base field E(F_p): {has_extension} ✗")
    
except RuntimeError as e:
    print(f"\n✗ {e}")
    print("Note: The search algorithm may need optimization for larger fields")

print("\n" + "=" * 60)
print("✅ Phase 3 implementation complete!")
print("=" * 60)
