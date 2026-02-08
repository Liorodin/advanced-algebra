import { useState } from 'react';
import type { BLSResponse } from '../types/bls';

interface StepByStepViewProps {
  result: BLSResponse;
}

interface StepSection {
  title: string;
  items: { label: string; value: string }[];
}

export function StepByStepView({ result }: StepByStepViewProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const sections: StepSection[] = [
    {
      title: 'Step 1: Curve Group',
      items: [
        { label: '|E(F_p)|', value: String(result.group_order) },
        { label: 'r (largest prime factor)', value: String(result.r) },
        { label: 'Cofactor (|G|/r)', value: String(result.cofactor) },
      ],
    },
    {
      title: 'Step 2: Extension Field',
      items: [
        { label: 'Embedding degree k', value: String(result.embedding_degree) },
        { label: 'Irreducible polynomial f(x)', value: result.irreducible_poly },
      ],
    },
    {
      title: 'Step 3: Hash-to-Point',
      items: [
        { label: 'H(m)', value: `(${result.hash_point.x}, ${result.hash_point.y})` },
      ],
    },
    {
      title: 'Step 4: Signature',
      items: [
        { label: 'sig = a * H(m)', value: `(${result.signature.x}, ${result.signature.y})` },
      ],
    },
    {
      title: 'Step 5: Public Point Q',
      items: [
        { label: 'Q', value: `(${result.Q.x}, ${result.Q.y})` },
      ],
    },
    {
      title: 'Step 6: Tate Pairing Verification',
      items: [
        { label: 'e_r(sig, Q)', value: result.pairing_lhs },
        { label: 'e_r(H(m), aQ)', value: result.pairing_rhs },
        { label: 'Match?', value: result.verified ? 'Yes' : 'No' },
      ],
    },
  ];

  const toggle = (i: number) => setOpenIndex(openIndex === i ? null : i);

  return (
    <div style={{
      backgroundColor: '#ffffff',
      padding: '24px',
      borderRadius: '12px',
      border: '1px solid #e2e8f0',
    }}>
      <h2 style={{ marginTop: 0, fontSize: '1.1rem', color: '#1e293b' }}>
        Step-by-Step Computation
      </h2>
      {sections.map((section, i) => (
        <div key={i} style={{
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          marginBottom: '8px',
          overflow: 'hidden',
        }}>
          <button
            onClick={() => toggle(i)}
            style={{
              width: '100%',
              padding: '12px 16px',
              background: openIndex === i ? '#f1f5f9' : '#ffffff',
              border: 'none',
              cursor: 'pointer',
              textAlign: 'left',
              fontSize: '0.95rem',
              fontWeight: 600,
              color: '#334155',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            {section.title}
            <span style={{ fontSize: '0.75rem' }}>{openIndex === i ? '▲' : '▼'}</span>
          </button>
          {openIndex === i && (
            <div style={{ padding: '12px 16px', borderTop: '1px solid #e2e8f0' }}>
              {section.items.map((item, j) => (
                <div key={j} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '6px 0',
                  borderBottom: j < section.items.length - 1 ? '1px solid #f1f5f9' : 'none',
                }}>
                  <span style={{ color: '#64748b', fontSize: '0.875rem' }}>{item.label}</span>
                  <span style={{ fontFamily: 'monospace', color: '#1e293b', fontSize: '0.875rem' }}>
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
