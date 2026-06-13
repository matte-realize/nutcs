import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Northeastern University Transfer Credits Search",
  description:
    "Search how courses from other institutions transfer as Northeastern University credit.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
