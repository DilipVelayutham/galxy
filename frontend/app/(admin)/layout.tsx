import '@/app/globals.css';
import { ReactNode } from 'react';
import Link from 'next/link';
import { NeonButton } from '@/components/ui/NeonButton';

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen bg-voidBlack text-textPrimary">
      {/* Sidebar */}
      <aside className="w-64 bg-panelCharcoal p-6 flex flex-col gap-4">
        <h1 className="text-2xl font-bold text-primaryNeon mb-6">Galxy Admin</h1>
        <nav className="flex-grow space-y-2">
          <Link href="/admin/categories">
            <NeonButton variant="primary" className="w-full justify-start">
              Categories
            </NeonButton>
          </Link>
          {/* Additional admin links can be added here */}
        </nav>
        <footer className="mt-auto text-xs text-textMuted">
          © 2026 Galxy. All rights reserved.
        </footer>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8 overflow-y-auto">{children}</main>
    </div>
  );
}
