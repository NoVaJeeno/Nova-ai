import type { Metadata } from "next";
import "./globals.css";
import { ClaudeProvider } from "../providers/ClaudeProvider";

export const metadata: Metadata = {
  title: "Claude System App",
  description: "Dein ultimatives Claude-gesteuertes Ökosystem.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de">
      <body>
        <ClaudeProvider>
          {children}
        </ClaudeProvider>
      </body>
    </html>
  );
}
