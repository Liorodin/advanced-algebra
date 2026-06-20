import { useState, useCallback, useEffect, useRef } from 'react';
import type { BLSRequest, BLSResponse } from '../types/bls';
import { runBLS } from '../api/bls';

interface UseBLSReturn {
  result: BLSResponse | null;
  error: string | null;
  loading: boolean;
  elapsed: number;
  execute: (params: BLSRequest) => Promise<void>;
  clear: () => void;
}

/** Custom hook for BLS signature operations. */
export function useBLS(): UseBLSReturn {
  const [result, setResult] = useState<BLSResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (loading) {
      setElapsed(0);
      timerRef.current = setInterval(() => setElapsed(s => s + 1), 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [loading]);

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

  return { result, error, loading, elapsed, execute, clear };
}
