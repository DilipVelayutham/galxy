import "./globals.css";

export const metadata = {
  title: "GALXY",
  description: "Customize and visualize your suspended floating product designs in real-time with neon glows and dynamic pricing.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
