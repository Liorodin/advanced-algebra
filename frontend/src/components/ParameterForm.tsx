import { useState } from 'react';
import type { BLSRequest } from '../types/bls';

interface ParameterFormProps {
  onSubmit: (params: BLSRequest) => void;
  loading: boolean;
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 12px',
  border: '1px solid #cbd5e1',
  borderRadius: '6px',
  fontSize: '0.95rem',
  boxSizing: 'border-box',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  marginBottom: '4px',
  fontSize: '0.875rem',
  fontWeight: 600,
  color: '#334155',
};

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
    <form onSubmit={handleSubmit} style={{
      backgroundColor: '#ffffff',
      padding: '24px',
      borderRadius: '12px',
      border: '1px solid #e2e8f0',
      marginBottom: '24px',
    }}>
      <h2 style={{ marginTop: 0, fontSize: '1.1rem', color: '#1e293b' }}>
        Parameters
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
        <div>
          <label style={labelStyle}>p (prime, p &#8801; 3 mod 4)</label>
          <input style={inputStyle} type="number" value={p} onChange={e => setP(e.target.value)} required />
        </div>
        <div>
          <label style={labelStyle}>A (curve coefficient)</label>
          <input style={inputStyle} type="number" value={A} onChange={e => setA(e.target.value)} required />
        </div>
        <div>
          <label style={labelStyle}>B (curve coefficient)</label>
          <input style={inputStyle} type="number" value={B} onChange={e => setB(e.target.value)} required />
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '16px', marginBottom: '20px' }}>
        <div>
          <label style={labelStyle}>Private key (a)</label>
          <input style={inputStyle} type="number" value={privateKey} onChange={e => setPrivateKey(e.target.value)} required />
        </div>
        <div>
          <label style={labelStyle}>Message</label>
          <input style={inputStyle} type="text" value={message} onChange={e => setMessage(e.target.value)} required />
        </div>
      </div>
      <button
        type="submit"
        disabled={loading}
        style={{
          padding: '10px 24px',
          backgroundColor: loading ? '#94a3b8' : '#2563eb',
          color: '#ffffff',
          border: 'none',
          borderRadius: '8px',
          fontSize: '0.95rem',
          fontWeight: 600,
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Computing...' : 'Sign & Verify'}
      </button>
    </form>
  );
}
