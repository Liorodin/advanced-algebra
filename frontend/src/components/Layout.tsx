import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <header className="bg-slate-800 text-slate-100 px-6 py-4 shadow-sm">
        <h1 className="m-0 text-2xl font-semibold">
          BLS Signature Scheme
        </h1>
        <p className="mt-1 mb-0 text-sm text-slate-400">
          Reduced Tate Pairing &mdash; Advanced Algebra &amp; Applications in Cryptography
        </p>
      </header>
      <main className="max-w-[960px] mx-auto my-6 px-6">
        {children}
      </main>
    </div>
  );
}
