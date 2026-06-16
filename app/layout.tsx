import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "../providers/AuthProvider";
import { StorageProvider } from "../providers/StorageProvider";
import { ToolProvider } from "../providers/ToolProvider";
import { ToolInitializer } from "../components/ToolInitializer";

export const metadata: Metadata = {
  title: "Ultimate Chat KI",
  description: "Deine ultimative Entwicklungsplattform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de">
      <body>
        <AuthProvider>
          <StorageProvider>
            <ToolProvider>
              <ToolInitializer />
              {children}
            </ToolProvider>
          </StorageProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
