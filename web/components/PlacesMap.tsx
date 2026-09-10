"use client";

// Renders a Topographia place list as a Leaflet map, matching Topographia's own pin
// tiers and colours (~/topographia-sacra/assets/edition.css). Loaded client-only via
// next/dynamic({ssr: false}) from Workbench.tsx -- Leaflet touches window/document
// directly and would break the static-export SSG pass otherwise.
//
// Per the plan: Leaflet from cdnjs (version-pinned), no npm dependency -- the static
// export has no bundler step for CSS from node_modules, so both the script and the
// stylesheet are injected as plain tags here, mirroring how Topographia's own site
// loads Leaflet. CARTO Voyager tiles, same attribution string as Topographia's
// assets/chapter.js.
import { useEffect, useRef } from "react";
import type { PlacesMapData } from "@/lib/data";

// Leaflet is loaded from cdnjs at runtime (no npm dependency -- see the plan), so
// there's no @types/leaflet package to import from. This is only the small slice of
// Leaflet's API this component actually calls.
type LatLngTuple = [number, number];
interface LeafletMap {
  remove(): void;
  setView(center: LatLngTuple, zoom: number): void;
  fitBounds(bounds: LatLngTuple[], opts?: { padding?: [number, number] }): void;
  invalidateSize(): void;
}
interface LeafletNS {
  map(el: HTMLElement, opts?: { scrollWheelZoom?: boolean }): LeafletMap;
  tileLayer(url: string, opts: { attribution: string; maxZoom?: number }): { addTo(m: LeafletMap): unknown };
  circleMarker(
    coords: LatLngTuple,
    opts: { radius: number; color: string; weight: number; fillColor: string; fillOpacity: number; dashArray?: string }
  ): { addTo(m: LeafletMap): { bindTooltip(text: string, opts?: { sticky?: boolean }): unknown } };
  polyline(coords: LatLngTuple[], opts: { color: string; weight: number; opacity: number; dashArray: string }): {
    addTo(m: LeafletMap): unknown;
  };
}

const LEAFLET_VERSION = "1.9.4";
const LEAFLET_JS = `https://cdnjs.cloudflare.com/ajax/libs/leaflet/${LEAFLET_VERSION}/leaflet.js`;
const LEAFLET_CSS = `https://cdnjs.cloudflare.com/ajax/libs/leaflet/${LEAFLET_VERSION}/leaflet.css`;

// Topographia's own pin palette (--pin-id / --pin-pr / --pin-cj / region), so a pin
// looks the same whether you're on Topographia or seeing it inline here.
const TIER_STYLE: Record<string, { fill: string; stroke: string; radius: number; dash?: string }> = {
  identified: { fill: "#274B5C", stroke: "#FBF7EA", radius: 7 },
  probable: { fill: "#5A8294", stroke: "#FBF7EA", radius: 7 },
  conjectural: { fill: "#FBF7EA", stroke: "#274B5C", radius: 6 },
  region: { fill: "rgba(122,90,58,0.18)", stroke: "#7A5A3A", radius: 6, dash: "3 2" },
};

let leafletLoading: Promise<void> | null = null;

function loadLeaflet(): Promise<void> {
  if (typeof window !== "undefined" && (window as unknown as { L?: unknown }).L) {
    return Promise.resolve();
  }
  if (leafletLoading) return leafletLoading;
  leafletLoading = new Promise((resolve, reject) => {
    if (!document.querySelector(`link[href="${LEAFLET_CSS}"]`)) {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = LEAFLET_CSS;
      document.head.appendChild(link);
    }
    const existing = document.querySelector<HTMLScriptElement>(`script[src="${LEAFLET_JS}"]`);
    if (existing) {
      existing.addEventListener("load", () => resolve());
      existing.addEventListener("error", () => reject(new Error("leaflet failed to load")));
      return;
    }
    const script = document.createElement("script");
    script.src = LEAFLET_JS;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("leaflet failed to load"));
    document.head.appendChild(script);
  });
  return leafletLoading;
}

export default function PlacesMap({ data }: { data: PlacesMapData }) {
  const elRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadLeaflet()
      .then(() => {
        if (cancelled || !elRef.current) return;
        const L = (window as unknown as { L: LeafletNS }).L;
        if (mapRef.current) {
          mapRef.current.remove();
          mapRef.current = null;
        }
        const map = L.map(elRef.current, { scrollWheelZoom: false });
        mapRef.current = map;
        L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
          attribution:
            '&copy; <a href="https://openstreetmap.org/">OpenStreetMap</a> contributors ' +
            '&copy; <a href="https://carto.com/">CARTO</a>',
          maxZoom: 19,
        }).addTo(map);

        const byKey: Record<string, [number, number]> = {};
        for (const p of data.places) {
          byKey[p.key] = p.coords;
          const style = TIER_STYLE[p.tier] || TIER_STYLE.identified;
          const marker = L.circleMarker(p.coords, {
            radius: style.radius,
            color: style.stroke,
            weight: 2,
            fillColor: style.fill,
            fillOpacity: p.tier === "region" ? 0.4 : 1,
            dashArray: style.dash,
          }).addTo(map);
          marker.bindTooltip(p.name, { sticky: true });
        }

        if (data.route && data.route.length >= 2) {
          const coords = data.route.map((k) => byKey[k]).filter(Boolean) as [number, number][];
          if (coords.length >= 2) {
            L.polyline(coords, { color: "#7A5A3A", weight: 2, opacity: 0.65, dashArray: "7 5" }).addTo(map);
          }
        }

        if (data.view) {
          map.setView(data.view.center, data.view.zoom);
        } else if (data.places.length) {
          map.fitBounds(data.places.map((p) => p.coords) as [number, number][], { padding: [24, 24] });
        } else {
          map.setView([31.8, 35.2], 7); // Levant fallback -- shouldn't be reached (no places = no panel)
        }
        // the panel can mount before its flex/grid parent settles its final width
        requestAnimationFrame(() => map.invalidateSize());
      })
      .catch(() => {
        // leaflet failed to load (offline, CDN blocked) -- the place list below the
        // map still renders from the same data, so nothing is lost, just the pins
      });
    return () => {
      cancelled = true;
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data.chapterUrl]);

  return <div className="places-map" ref={elRef} aria-label={data.title ? `Map: ${data.title}` : "Map"} />;
}
