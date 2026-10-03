import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const toknSans = localFont({
  src: [
    {
      path: "../../public/fonts/plus-jakarta-sans/plus-jakarta-sans-latin-400-normal.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../public/fonts/plus-jakarta-sans/plus-jakarta-sans-latin-500-normal.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../../public/fonts/plus-jakarta-sans/plus-jakarta-sans-latin-600-normal.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "../../public/fonts/plus-jakarta-sans/plus-jakarta-sans-latin-700-normal.woff2",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-tokn-sans",
  display: "swap",
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
