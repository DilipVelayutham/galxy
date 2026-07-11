import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  activeTab?: string;
}

export default function Layout({ children, title, activeTab }: LayoutProps) {
  return (
    <div className="min-h-screen bg-voidBlack text-textPrimary">
      <header className="bg-panelCharcoal border-b border-white/10 px-6 py-4">
        <h1 className="text-xl font-bold font-poppins">{title || 'Admin Dashboard'}</h1>
      </header>
      <main className="p-6">
        {children}
      </main>
    </div>
  );
}
