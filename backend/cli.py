from app.crypto.bls import BLSSignatureScheme

def main():
    print("="*50)
    print("BLS Signature Scheme - Interactive CLI")
    print("="*50)
    
    try:
        # User input matching the assignment requirements
        p_str = input("Enter a prime number <p>: ")
        A_str = input("Enter elliptic curve parameter A=<A>: ")
        B_str = input("Enter elliptic curve parameter B=<B>: ")
        a_str = input("Enter private key <a>: ")
        m = input("Enter Alice's message <m>: ")
        
        # Convert inputs to integers
        p = int(p_str)
        A = int(A_str)
        B = int(B_str)
        a = int(a_str)
        
        print("\n" + "="*50)
        print("COMPUTING BLS SIGNATURE SCHEME")
        print("="*50)
        
        # Initialize the BLS system
        bls = BLSSignatureScheme(p=p, A=A, B=B, private_key=a)
        
        # Execute signing and verification steps
        steps = bls.get_steps(m)
        
        # Display cryptographic structures
        print(f"\n CRYPTOGRAPHIC STRUCTURES")
        print("-" * 50)
        print(f"Prime field: F_{p}")
        print(f"Elliptic curve: y² = x³ + {A}x + {B}")
        print(f"Group order |E(F_p)|: {steps['group_order']}")
        print(f"Largest prime factor r: {steps['r']}")
        print(f"Cofactor: {steps['cofactor']}")
        print(f"Embedding degree k: {steps['embedding_degree']}")
        print(f"Irreducible polynomial f(x): {steps['irreducible_poly']}")
        
        # Display signing process
        print(f"\n SIGNING PROCESS")
        print("-" * 50)
        print(f"Message: '{m}'")
        print(f"\n1. Hash-to-Point:")
        print(f"   H(m) = ({steps['hash_point']['x']}, {steps['hash_point']['y']})")
        
        print(f"\n2. Signature Computation:")
        print(f"   σ = a · H(m)")
        print(f"   σ = {a} · H(m)")
        print(f"   σ = ({steps['signature']['x']}, {steps['signature']['y']})")
        
        print(f"\n3. Public Key Setup:")
        print(f"   Q ∈ E(F_{{p^k}}) = ({steps['Q']['x']}, {steps['Q']['y']})")
        
        # Display verification process
        print(f"\n VERIFICATION PROCESS")
        print("-" * 50)
        print(f"Computing pairings:")
        print(f"  LHS: e_r(σ, Q) = {steps['pairing_lhs']}")
        print(f"  RHS: e_r(H(m), aQ) = {steps['pairing_rhs']}")
        
        print(f"\nVerification equation: e_r(aH(m), Q) = e_r(H(m), aQ)")
        
        # Final result
        print("\n" + "="*50)
        if steps['verified']:
            print("✓ VERIFICATION SUCCESSFUL!")
            print(f"Alice's message: '{m}' was received and verified")
            print(f"Both pairings match: {steps['pairing_lhs']}")
        else:
            print(f"Alice's message: '{m}' was **NOT verified**! Pairing values differ.")
            print(f"Left side: {steps['pairing_lhs']}")
            print(f"Right side: {steps['pairing_rhs']}")
            
    except ValueError as e:
        print(f"\nError: Please ensure you entered valid integers. Details: {e}")
    except Exception as e:
        print(f"\nMathematical or Algorithmic Error: {e}")

if __name__ == "__main__":
    main()