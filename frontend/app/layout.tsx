import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RouteCraft AI — Aurora Campus Navigator",
  description: "Intelligent campus navigation, Dijkstra shortest-path calculations, and grounded AI assistant for Aurora University.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-sans bg-slate-50 text-slate-800 antialiased selection:bg-blue-100 selection:text-blue-900">
        {children}
      </body>
    </html>
  );
}
