# Testing Guide — BLS Signature Scheme

This document explains how to run every layer of the test suite:
unit tests, property tests with random primes, and E2E frontend tests.

---

## Running the app

Two terminals — one for the backend, one for the frontend.

**Terminal 1 — backend (FastAPI on port 8000):**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --port 8000
```

**Terminal 2 — frontend (Vite dev server on port 5173):**
```bash
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173** in your browser.

Enter parameters (default: p=103, A=1, B=0, private key=7, message=שלום) and click **Sign & Verify**.

> **Tip — pairing-friendly parameters** (small embedding degree, fast):
> | p | A | B | r | k |
> |---|---|---|---|---|
> | 103 | 1 | 0 | 13 | 2 | ← assignment example |
> | 283 | 1 | 0 | 71 | 2 | larger, still fast |
> | 211 | 1 | 4 | 113 | 4 | slower |
>
> Avoid random large primes — most have huge embedding degree k and will hang.

---

## Quick start

```bash
# Backend unit + property tests (no servers needed)
cd backend
pip install -r requirements.txt
pytest tests/ --ignore=tests/test_routes_bls.py --ignore=tests/test_main.py

# E2E tests (starts both servers automatically)
cd frontend
npm install
npx playwright install chromium
npx playwright test
```

---

## 1. Backend unit tests

**Location:** `backend/tests/`  
**Framework:** pytest

### Run all unit tests

```bash
cd backend
pytest tests/ --ignore=tests/test_routes_bls.py --ignore=tests/test_main.py -v
```

> `test_routes_bls.py` and `test_main.py` require FastAPI/httpx to be installed.
> Install with `pip install fastapi httpx` to include them.

### Run a single test file

```bash
pytest tests/test_prime_field.py -v
pytest tests/test_bls.py -v
```

### Run a single test

```bash
pytest tests/test_bls.py::TestBLSSign::test_assignment_signature -v
```

### Test files

| File | Module | Tests |
|------|--------|-------|
| `test_utils.py` | `utils` | gcd, extended_gcd, is_prime, prime_factors, largest_prime_factor |
| `test_prime_field.py` | `prime_field` | PrimeField, FieldElement arithmetic |
| `test_polynomial.py` | `polynomial` | Polynomial arithmetic, GCD, irreducibility |
| `test_elliptic_curve.py` | `elliptic_curve` | EllipticCurve, ECPoint group law |
| `test_extension_field.py` | `extension_field` | ExtensionField, ExtFieldElement |
| `test_ext_curve.py` | `ext_curve` | ExtCurvePoint, find_point_of_order_r |
| `test_hash_to_point.py` | `hash_to_point` | string_to_field_element, hash_to_point |
| `test_miller.py` | `miller` | line_function, Miller's algorithm |
| `test_bls.py` | `bls` | BLSSignatureScheme: sign, verify, tate_pairing |
| `test_routes_bls.py` | `routes.bls` | POST /api/bls/run (needs FastAPI) |
| `test_main.py` | `main` | Health check (needs FastAPI) |
| `test_comprehensive.py` | all modules | 447 thorough unit tests |

---

## 2. Property tests with randomly generated primes

**Location:** `backend/tests/test_random_primes.py`

These tests generate random primes ≡ 3 (mod 4) and verify mathematical
properties across all of them — a good way to find edge cases.

### Run with defaults (random seed, printed for reproducibility)

```bash
cd backend
pytest tests/test_random_primes.py -v
```

Output includes the seed used, e.g.:
```
[test_random_primes] random seed=2847361928  (rerun with TEST_SEED=2847361928 to reproduce)
```

### Configuration — command-line options

| Option | Description | Default |
|--------|-------------|---------|
| `--prime-limit N` | Upper bound for prime generation | 400 |
| `--n-primes N` | How many random primes to sample | 30 |
| `--test-seed N` | RNG seed (omit for fresh random) | random |

```bash
# Bigger exploration — more primes, larger field sizes
pytest tests/test_random_primes.py --prime-limit 1000 --n-primes 60 -v

# Exact reproduction of a previous run
pytest tests/test_random_primes.py --test-seed 2847361928 -v

# Quick smoke run
pytest tests/test_random_primes.py --prime-limit 100 --n-primes 5 -v
```

### Configuration — environment variables

Equivalent to CLI options, useful in CI:

```bash
TEST_PRIME_LIMIT=1000 TEST_N_PRIMES=60 TEST_SEED=42 pytest tests/test_random_primes.py
```

CLI options take precedence over environment variables.

### What is tested across random primes

- **Field arithmetic:** Fermat's little theorem, closure, commutativity,
  associativity, distributivity, every non-zero element has an inverse,
  quadratic residue count = (p−1)/2, sqrt roundtrip, Wilson's theorem
- **Polynomial arithmetic:** Division algorithm, GCD divides both inputs,
  extended GCD Bézout identity, degree of product, make_monic
- **Elliptic curve group law:** Identity, negation, doubling on curve,
  Hasse bound, scalar mult distributive, order divides group order,
  all small multiples lie on curve
- **BLS round-trips:** Sign + verify for multiple keys and messages,
  bilinearity of Tate pairing, wrong key fails verification
- **Edge-case primes:** p = 3, 7, 11 (exhaustive), primes near 2^6, 2^7, 2^8

---

## 3. E2E frontend tests

**Location:** `frontend/e2e/bls.spec.ts`  
**Framework:** Playwright

Playwright starts both the backend (uvicorn on port 8000) and frontend
(Vite dev server on port 5173) automatically before running tests.

### Prerequisites

```bash
# Install Node dependencies
cd frontend
npm install

# Download Playwright browsers (first time only)
npx playwright install chromium
```

Backend must be installable:
```bash
cd backend
pip install -r requirements.txt
```

### Run all E2E tests

```bash
cd frontend
npx playwright test
```

### Run with a visible browser (headed mode)

```bash
npx playwright test --headed
```

### Run a single test file

```bash
npx playwright test e2e/bls.spec.ts
```

### Run a single test by name

```bash
npx playwright test -g "shows Signature Verified after submit"
```

### Show the HTML report after a run

```bash
npx playwright show-report
```

### E2E test categories

| Category | What is tested |
|----------|----------------|
| **Page load** | Header, form visibility, default values, button state |
| **Loading state** | Button disabled + shows "Computing…" during request |
| **Assignment example** | p=103 A=1 B=0 key=7 msg=שלום → sig=(18,44), H(m)=(32,47), pairing verified |
| **Step-by-step accordion** | Group order 104, r=13, k=2, irreducible poly, one section open at a time |
| **Error handling** | Invalid prime, singular curve, composite p, error dismiss button |
| **API mocked responses** | Verified, failed, 400 error, network failure — no backend needed |
| **Different parameters** | Private key 2, different messages sent correctly to API |
| **Accessibility** | Labels, keyboard navigation, heading structure |

### Reusing running servers

If the backend and frontend are already running, Playwright will reuse them
(`reuseExistingServer: true` in `playwright.config.ts`). This makes re-runs fast.

```bash
# Terminal 1 — backend
cd backend && uvicorn main:app --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev

# Terminal 3 — run tests against already-running servers
cd frontend && npx playwright test
```

---

## 4. Running everything at once

```bash
cd backend

# All unit + property tests
pytest tests/ --ignore=tests/test_routes_bls.py --ignore=tests/test_main.py -q

# E2E (from frontend/)
cd ../frontend && npx playwright test
```

Expected results:

| Suite | Count | Notes |
|-------|-------|-------|
| Unit tests (`test_comprehensive.py`) | 447 pass | |
| Property tests (`test_random_primes.py`) | ~1169 pass, 3 skip | skips = degenerate BLS cases |
| Original unit tests | ~137 pass, 1 fail | pre-existing hash collision on p=103 |
| E2E (mocked) | fast, no servers needed | uses `page.route()` |
| E2E (live) | requires both servers | assignment values verified end-to-end |

---

## 5. Known issues

| Issue | File | Notes |
|-------|------|-------|
| `test_different_messages_different_points` | `test_hash_to_point.py` | Hash collision with p=103 (only 13 possible hash outputs). Not a code bug. |
| `test_routes_bls.py` / `test_main.py` | — | Need `pip install fastapi httpx` |
