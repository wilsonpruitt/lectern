import type { MetadataRoute } from "next";
import { allOccasions, YEARS } from "@/lib/data";
import { allRefKeys } from "@/lib/greek";

const BASE = "https://lectern.wrootpress.com";

// Mirrors the generateStaticParams of every route so the sitemap and the
// exported pages cannot drift apart. next.config sets trailingSlash: true,
// so every URL here carries one.
export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const urls: string[] = ["/", "/greek/"];

  for (const o of allOccasions()) {
    urls.push(`/${o.occasion.id}/`);
  }

  for (const y of YEARS) {
    urls.push(`/year/${y.toLowerCase()}/`);
    urls.push(`/series/${y.toLowerCase()}/`);
  }

  for (const ref of allRefKeys()) {
    urls.push(`/greek/${ref}/`);
  }

  return urls.map((url) => ({ url: `${BASE}${url}` }));
}
