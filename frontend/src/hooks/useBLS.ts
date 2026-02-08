import { useState, useCallback } from 'react';
import type { BLSRequest, BLSResponse } from '../types/bls';
import { runBLS } from '../api/bls';

interface UseBLSReturn {
  result: BLSResponse | null;
  error: string | null;
  loading: boolean;
  execute: (params: BLSRequest) => Promise<void>;
  clear: () => void;
}

/** Custom hook for BLS signature operations. */
export function useBLS(): UseBLSReturn {
  const [result, setResult] = useState<BLSResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const execute = useCallback(async (params: BLSRequest) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await runBLS(params);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, error, loading, execute, clear };
}
