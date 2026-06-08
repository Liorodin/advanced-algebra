import { useState } from 'react';
import type { BLSRequest } from '../types/bls';

interface ParameterFormProps {
  onSubmit: (params: BLSRequest) => void;
  loading: boolean;
  elapsed: number;
}

export function ParameterForm({ onSubmit, loading, elapsed }: ParameterFormProps) {
  const [p, setP] = useState('103');
  const [A, setA] = useState('1');
  const [B, setB] = useState('0');
  const [privateKey, setPrivateKey] = useState('7');
  const [message, setMessage] = useState('שלום');
  const [k, setK] = useState('');
  const [seed, setSeed] = useState('42');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Parameters<typeof onSubmit>[0] = {
      p: parseInt(p, 10),
      A: parseInt(A, 10),
      B: parseInt(B, 10),
      private_key: parseInt(privateKey, 10),
      message,
    };
    if (k.trim() !== '') payload.k = parseInt(k, 10);
    payload.seed = parseInt(seed, 10);
    onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl border border-slate-200 mb-6">
      <h2 className="mt-0 text-lg text-slate-800">
        Parameters
      </h2>
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block mb-1 text-sm font-semibold text-slate-700">p (prime, p &#8801; 3 mod 4)</label>
          <input className="w-full px-3 py-2 border border-slate-300 rounded-md text-[0.95rem]" type="number" value={p} onChange={e => setP(e.target.value)} required />
        </div>
        <div>
          <label className="block mb-1 text-sm font-semibold text-slate-700">A (curve coefficient)</label>
          <input className="w-full px-3 py-2 border border-slate-300 rounded-md text-[0.95rem]" type="number" value={A} onChange={e => setA(e.target.value)} required />
        </div>
        <div>
          <label className="block mb-1 text-sm font-semibold text-slate-700">B (curve coefficient)</label>
          <input className="w-full px-3 py-2 border border-slate-300 rounded-md text-[0.95rem]" type="number" value={B} onChange={e => setB(e.target.value)} required />
        </div>
      </div>
      <div className="grid grid-cols-[1fr_1fr_1fr_2fr] gap-4 mb-5">
        <div>
          <label className="block mb-1 text-sm font-semibold text-slate-700">Private key (a)</label>
          <input className="w-full px-3 py-2 border border-slate-300 rounded-md text-[0.95rem]" type="number" value={privateKey} onChange={e => setPrivateKey(e.target.value)} required />
        </div>
        <div>
          <label className="block mb-1 text-sm font-semibold text-slate-700">Seed</label>
          <input className="w-full px-3 py-2 border border-slate-300 rounded-md text-[0.95rem]" type="number" value={seed} onChange={e => setSeed(e.target.value)} required />
        </div>
        <div>
          <label className="block mb-1 text-sm font-semibold text-slate-700">Embedding degree k</label>
          <input className="w-full px-3 py-2 border border-slate-300 rounded-md text-[0.95rem]" type="number" min="2" value={k} onChange={e => setK(e.target.value)} placeholder="auto" />
          {k !== '' && parseInt(k, 10) > 2 && (
            <p className="mt-1 text-xs text-amber-600">
              k={k} uses F<sub>p<sup>{k}</sup></sub> — cofactor ≈ p<sup>{k}</sup>/r, expect slow computation
            </p>
          )}
        </div>
        <div>
          <label className="block mb-1 text-sm font-semibold text-slate-700">Message</label>
          <input className="w-full px-3 py-2 border border-slate-300 rounded-md text-[0.95rem]" type="text" value={message} onChange={e => setMessage(e.target.value)} required />
        </div>
      </div>
      <button
        type="submit"
        disabled={loading}
        className={`px-6 py-2.5 text-white border-none rounded-lg text-[0.95rem] font-semibold ${
          loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-blue-600 cursor-pointer hover:bg-blue-700'
        }`}
      >
        {loading ? `Computing... ${elapsed}s` : 'Sign & Verify'}
      </button>
    </form>
  );
}
