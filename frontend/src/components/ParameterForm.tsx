import { useState } from 'react';
import type { BLSRequest } from '../types/bls';

interface ParameterFormProps {
  onSubmit: (params: BLSRequest) => void;
  loading: boolean;
}

export function ParameterForm({ onSubmit, loading }: ParameterFormProps) {
  const [p, setP] = useState('103');
  const [A, setA] = useState('1');
  const [B, setB] = useState('0');
  const [privateKey, setPrivateKey] = useState('7');
  const [message, setMessage] = useState('שלום');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      p: parseInt(p, 10),
      A: parseInt(A, 10),
      B: parseInt(B, 10),
      private_key: parseInt(privateKey, 10),
      message,
    });
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
      <div className="grid grid-cols-[1fr_2fr] gap-4 mb-5">
        <div>
          <label className="block mb-1 text-sm font-semibold text-slate-700">Private key (a)</label>
          <input className="w-full px-3 py-2 border border-slate-300 rounded-md text-[0.95rem]" type="number" value={privateKey} onChange={e => setPrivateKey(e.target.value)} required />
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
        {loading ? 'Computing...' : 'Sign & Verify'}
      </button>
    </form>
  );
}
