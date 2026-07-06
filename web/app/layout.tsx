import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://lectern.wrootpress.com"),
  title: "Lectern — a preacher's workbench",
  description:
    "The lectionary is a deck of series waiting to be dealt. Lectern is a workbench over the church year: the day's readings anchored, with Wesley sermon companions, hymn recommendations, and calls to worship arranged around them.",
  icons: { icon: "/assets/favicon.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <script defer src="/_vercel/insights/script.js"></script>
      </head>
      <body>{children}</body>
    </html>
  );
}
