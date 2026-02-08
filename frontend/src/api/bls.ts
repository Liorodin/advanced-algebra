import type { BLSRequest, BLSResponse, APIError } from '../types/bls';

const API_BASE = '/api';

/** Run the full BLS signature pipeline. */
export async function runBLS(params: BLSRequest): Promise<BLSResponse> {
  const response = await fetch(`${API_BASE}/bls/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error: APIError = await response.json();
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/** Check backend health. */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: HTTP ${response.status}`);
  }
  return response.json();
}
