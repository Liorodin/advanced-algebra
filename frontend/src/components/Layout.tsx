import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    }}>
      <header style={{
        backgroundColor: '#1e293b',
        color: '#f1f5f9',
        padding: '16px 24px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>
          BLS Signature Scheme
        </h1>
        <p style={{ margin: '4px 0 0', fontSize: '0.875rem', color: '#94a3b8' }}>
          Reduced Tate Pairing &mdash; Advanced Algebra &amp; Applications in Cryptography
        </p>
      </header>
      <main style={{
        maxWidth: '960px',
        margin: '24px auto',
        padding: '0 24px',
      }}>
        {children}
      </main>
    </div>
  );
}
