/** Point on an elliptic curve (coordinates as strings for extension field display). */
export interface PointResponse {
  x: string;
  y: string;
}

/** Request payload for the BLS signature pipeline. */
export interface BLSRequest {
  p: number;
  A: number;
  B: number;
  private_key: number;
  message: string;
}

/** Response from the BLS signature pipeline with all intermediate steps. */
export interface BLSResponse {
  group_order: number;
  r: number;
  cofactor: number;
  embedding_degree: number;
  irreducible_poly: string;
  hash_point: PointResponse;
  signature: PointResponse;
  Q: PointResponse;
  pairing_lhs: string;
  pairing_rhs: string;
  verified: boolean;
  display_message: string;
}

/** API error response. */
export interface APIError {
  detail: string;
}
