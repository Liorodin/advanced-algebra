# BLS Signature Scheme — Web App

Implementation of the **BLS signature scheme** using the **Reduced Tate Pairing**, built as a final assignment for *Advanced Algebra & Applications in Cryptography*.

## Project Structure

```
backend/          Python (FastAPI) — cryptographic logic + API
frontend/         React + TypeScript (Vite) — interactive UI
```

## Prerequisites

- **Python** 3.12+
- **Node.js** 18+
- **npm** 9+

## Setup & Run

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at **http://localhost:8000**.

- Health check: `GET /api/health`
- BLS pipeline: `POST /api/bls/run`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at **http://localhost:5173**. API requests are proxied to the backend automatically.

## Usage

1. Start both the backend and frontend.
2. Open **http://localhost:5173** in a browser.
3. Enter parameters (defaults are pre-filled from the assignment example):
   - **p** = 103, **A** = 1, **B** = 0, **a** = 7, **message** = "שלום"
4. Click **Sign & Verify**.
5. View the signature, verification result, and step-by-step intermediate values.

## Expected Output (Assignment Example)

| Parameter | Value |
|---|---|
| \|E(F\_p)\| | 104 |
| r | 13 |
| Cofactor | 8 |
| Embedding degree k | 2 |
| f(x) | x² + 1 |
| H(m) | (32, 47) |
| Signature | (18, 44) |
| Q | (8i, 47 + 56i) |
| e₁₃(aH(m), Q) | 22 + 49i |
| e₁₃(H(m), aQ) | 22 + 49i |

## Implementation Status

All cryptographic functions are currently **stubs** (`raise NotImplementedError`) with detailed docstrings. The team can divide and implement them following this order:

| Phase | Files | Depends On |
|---|---|---|
| 1 | `utils.py`, `prime_field.py` | Nothing |
| 2 | `polynomial.py` | Phase 1 |
| 3 | `elliptic_curve.py` | Phase 1 |
| 4 | `extension_field.py`, `ext_curve.py` | Phases 1 + 2 |
| 5 | `hash_to_point.py`, `miller.py` | Phases 1 + 3 |
| 6 | `bls.py` (orchestration) | All above |

The frontend and API layer are fully functional — once stubs are implemented, everything connects end-to-end.

## API Reference

### `POST /api/bls/run`

**Request:**
```json
{
  "p": 103,
  "A": 1,
  "B": 0,
  "private_key": 7,
  "message": "שלום"
}
```

**Response:** Returns group order, r, cofactor, embedding degree, irreducible polynomial, H(m), signature, Q, both pairing values, and verification result.

**Error codes:**
- `400` — Invalid parameters
- `501` — Stub not yet implemented
- `500` — Internal error
