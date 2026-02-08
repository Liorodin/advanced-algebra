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
    <div className="bg-white p-6 rounded-xl border border-slate-200">
      <h2 className="mt-0 text-lg text-slate-800">
        Step-by-Step Computation
      </h2>
      {sections.map((section, i) => (
        <div key={i} className="border border-slate-200 rounded-lg mb-2 overflow-hidden">
          <button
            onClick={() => toggle(i)}
            className={`w-full px-4 py-3 border-none cursor-pointer text-left text-[0.95rem] font-semibold text-slate-700 flex justify-between items-center ${
              openIndex === i ? 'bg-slate-100' : 'bg-white'
            }`}
          >
            {section.title}
            <span className="text-xs">{openIndex === i ? '▲' : '▼'}</span>
          </button>
          {openIndex === i && (
            <div className="px-4 py-3 border-t border-slate-200">
              {section.items.map((item, j) => (
                <div key={j} className={`flex justify-between py-1.5 ${
                  j < section.items.length - 1 ? 'border-b border-slate-100' : ''
                }`}>
                  <span className="text-slate-500 text-sm">{item.label}</span>
                  <span className="font-mono text-slate-800 text-sm">
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
