import type { Metadata } from "next";
import type { ReactNode } from "react";
import { QueryProvider } from "../components/admin/QueryProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "GALXY Admin Reviews",
  description: "Admin moderation and testimonials manager for GALXY.",
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className="dark">
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
