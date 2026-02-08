import type { BLSResponse } from '../types/bls';

interface ResultsDisplayProps {
  result: BLSResponse;
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  return (
    <div style={{
      backgroundColor: '#ffffff',
      padding: '24px',
      borderRadius: '12px',
      border: '1px solid #e2e8f0',
      marginBottom: '24px',
    }}>
      <h2 style={{ marginTop: 0, fontSize: '1.1rem', color: '#1e293b' }}>
        Results
      </h2>

      <div style={{
        padding: '16px',
        borderRadius: '8px',
        backgroundColor: result.verified ? '#f0fdf4' : '#fef2f2',
        border: `1px solid ${result.verified ? '#bbf7d0' : '#fecaca'}`,
        marginBottom: '16px',
      }}>
        <p style={{
          margin: 0,
          fontWeight: 600,
          color: result.verified ? '#166534' : '#991b1b',
          fontSize: '1rem',
        }}>
          {result.verified ? 'Signature Verified' : 'Verification Failed'}
        </p>
        <p style={{ margin: '8px 0 0', color: '#374151' }}>
          {result.display_message}
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <InfoCard label="Signature" value={`(${result.signature.x}, ${result.signature.y})`} />
        <InfoCard label="H(m)" value={`(${result.hash_point.x}, ${result.hash_point.y})`} />
        <InfoCard label="e_r(sig, Q)" value={result.pairing_lhs} />
        <InfoCard label="e_r(H(m), aQ)" value={result.pairing_rhs} />
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div style={{
      padding: '12px',
      backgroundColor: '#f8fafc',
      borderRadius: '6px',
      border: '1px solid #e2e8f0',
    }}>
      <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600, marginBottom: '4px' }}>
        {label}
      </div>
      <div style={{ fontSize: '0.95rem', color: '#1e293b', fontFamily: 'monospace', wordBreak: 'break-all' }}>
        {value}
      </div>
    </div>
  );
}
