# BLS Signature Scheme using Reduced Tate Pairing

Implementation of the **BLS signature scheme** using the **Reduced Tate Pairing**, built as a final assignment for the *Advanced Algebra & Applications in Cryptography* course.


## Project Structure
The project features a full-stack architecture alongside a required CLI interface:
```text
backend/          Python (FastAPI) — Core cryptographic logic + API
frontend/         React + TypeScript (Vite) — Interactive Web UI
cli.py           Interactive Command Line Interface (Assignment Requirement)
```

### Prerequisites
1. Python 3.12+ (with pipenv installed)

2. Node.js 18+ and npm 9+

### Setup & Run
The project provides two distinct ways to interact with the BLS scheme.

1. **Interactive CLI (Required by Assignment)**

To run the interactive command-line interface and manually enter the parameters ($p, A, B, a, m$) directly in your terminal:

```bash 
    cd backend
    pipenv install
    pipenv run python cli.py
```

2. **Interactive Web UI**

A complete graphical interface is provided to visualize the step-by-step mathematical computation.

**Step A: Start the Backend API** (Open Terminal 1)

```bash 
    cd backend
    pipenv install
    pipenv run uvicorn main:app --reload
```

The API will be available at http://localhost:8000.

**Step B: Start the Frontend UI** (Open Terminal 2)
```bash 
    cd frontend
    npm install
    npm run dev
```

Open http://localhost:5173 in your browser to use the app.

### Mathematical Implementation Details

The project implements all necessary mathematical primitives from scratch without relying on external cryptographic libraries:

1. **Prime Field Arithmetic ($F_p$)**: Implemented in prime_field.py. Includes the Euclidean extended algorithm for modular inverses and square roots for $p \equiv 3 \pmod 4$.

2. **Polynomials & Extension Fields ($F_{p^k}$):** Implemented in polynomial.py and extension_field.py. Uses Rabin's test for polynomial irreducibility and dynamically computes the embedding degree $k$.

3. **Elliptic Curves $E(F_p)$ & $E(F_{p^k})$:** Implemented in elliptic_curve.py and ext_curve.py. Implements the Double-and-Add algorithm for efficient scalar multiplication.

4. **Hash-to-Point ($H(m)$):** Implemented in hash_to_point.py. Converts strings using Windows-1255 encoding to base-256 integers, uses the Try-and-Increment method to find a valid $x$-coordinate, and applies Cofactor Clearing to map it to the subgroup of order $r$.

5. **Miller's Algorithm & Pairing:** Implemented in miller.py. Computes the Miller function $f_{r,P}(Q)$ using the binary expansion of $r$ and performs the final exponentiation to obtain the Reduced Tate Pairing.

6. **BLS Scheme:** Orchestrated in bls.py. Generates keys, signs messages ($\sigma = a \cdot H(m)$), and verifies signatures using bilinearity ($e_r(\sigma, Q) = e_r(H(m), aQ)$).