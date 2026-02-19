# Backend unit tests (TDD style)

Unit tests for all backend modules. Written in **TDD style**: tests define the expected behavior; they will **fail** until the corresponding code is implemented, then turn **green**.

## Run tests

From the `backend` directory:

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Or with more detail:

```bash
pytest tests/ -v --tb=short
```

## Structure

| Test file | Covers |
|-----------|--------|
| `test_utils.py` | `app.crypto.utils`: gcd, extended_gcd, is_prime, prime_factors, largest_prime_factor |
| `test_prime_field.py` | `app.crypto.prime_field`: PrimeField, FieldElement |
| `test_polynomial.py` | `app.crypto.polynomial`: Polynomial |
| `test_elliptic_curve.py` | `app.crypto.elliptic_curve`: EllipticCurve, ECPoint |
| `test_extension_field.py` | `app.crypto.extension_field`: ExtensionField, ExtFieldElement |
| `test_ext_curve.py` | `app.crypto.ext_curve`: ExtCurvePoint, find_point_of_order_r |
| `test_hash_to_point.py` | `app.crypto.hash_to_point`: string_to_field_element, increment_and_try, cofactor_clear, hash_to_point |
| `test_miller.py` | `app.crypto.miller`: line_function, miller |
| `test_bls.py` | `app.crypto.bls`: BLSSignatureScheme |
| `test_routes_bls.py` | `app.routes.bls`: POST /api/bls/run |
| `test_main.py` | Health check, app config |

## Dependencies

Tests use **pytest**, **pytest-asyncio**, and **httpx** (for FastAPI TestClient). These are listed in `requirements.txt`.
