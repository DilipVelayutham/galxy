import './globals.css';
import React from 'react';

export const metadata = {
  title: 'GALXY Studio - Admin Dashboard',
  description: 'Admin Dashboard and Analytics for GALXY Studio',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
