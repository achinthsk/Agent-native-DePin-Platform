import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const toknSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-tokn-sans",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Tokn Investments",
  description:
    "Investment intelligence and verification for tokenized infrastructure / DePIN / RWA assets.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${toknSans.variable} ${toknSans.className}`}>
      <body className="antialiased font-sans">{children}</body>
    </html>
  );
}
