import type { BLSResponse } from '../types/bls';

interface ResultsDisplayProps {
  result: BLSResponse;
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 mb-6">
      <h2 className="mt-0 text-lg text-slate-800">
        Results
      </h2>

      <div className={`p-4 rounded-lg mb-4 border ${
        result.verified
          ? 'bg-green-50 border-green-200'
          : 'bg-red-50 border-red-200'
      }`}>
        <p className={`m-0 font-semibold text-base ${
          result.verified ? 'text-green-800' : 'text-red-800'
        }`}>
          {result.verified ? 'Signature Verified' : 'Verification Failed'}
        </p>
        <p className="mt-2 mb-0 text-gray-700">
          {result.display_message}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
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
    <div className="p-3 bg-slate-50 rounded-md border border-slate-200">
      <div className="text-xs text-slate-500 font-semibold mb-1">
        {label}
      </div>
      <div className="text-[0.95rem] text-slate-800 font-mono break-all">
        {value}
      </div>
    </div>
  );
}
