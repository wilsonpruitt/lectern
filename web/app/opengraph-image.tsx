import { ImageResponse } from "next/og";

// Social-share card for Lectern. Fen & Ink: parchment ground, deep fen wordmark,
// reed accent + a small diamond fleuron (the ❦ glyph renders as tofu in satori, so
// it's drawn). Lectern in EB Garamond, the house thesis as the tagline.
export const runtime = "nodejs";
export const dynamic = "force-static"; // required for output: export
export const alt =
  "Lectern — a preacher's workbench over the church year · Wroot Press";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const IVORY = "#FBF8F1";
const FEN = "#2C3E4A";
const FEN_MIST = "#5B6B76";
const REED = "#C9A86A";
const QUIET = "#7A7E81";

// Subset EB Garamond to just the glyphs the card uses.
async function garamond(text: string, weight: 500 | 400, italic: boolean) {
  const ital = italic ? "1" : "0";
  const css = await (
    await fetch(
      `https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@${ital},${weight}&text=${encodeURIComponent(
        text
      )}`,
      { headers: { "User-Agent": "Mozilla/5.0" } }
    )
  ).text();
  const url = css.match(/src: url\((.+?)\) format\(['"]?(opentype|truetype)['"]?\)/);
  if (!url) throw new Error("font url not found");
  return (await fetch(url[1])).arrayBuffer();
}

export default async function Image() {
  const wordmark = "Lectern";
  const tagline = "the lectionary is a deck of series waiting to be dealt";
  const press = "A WROOT PRESS WORKBENCH";
  let fonts;
  try {
    const [medium, italic] = await Promise.all([
      garamond(wordmark + press, 500, false),
      garamond(tagline, 400, true),
    ]);
    fonts = [
      { name: "Garamond", data: medium, weight: 500 as const, style: "normal" as const },
      { name: "Garamond", data: italic, weight: 400 as const, style: "italic" as const },
    ];
  } catch {
    fonts = undefined; // fall back to satori's default serif metrics
  }

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: IVORY,
          fontFamily: "Garamond, Georgia, serif",
        }}
      >
        {/* inset printed-frame border */}
        <div
          style={{
            position: "absolute",
            top: 36,
            left: 36,
            right: 36,
            bottom: 36,
            border: `1px solid ${REED}`,
          }}
        />

        {/* diamond fleuron */}
        <div
          style={{
            width: 18,
            height: 18,
            background: REED,
            transform: "rotate(45deg)",
            marginBottom: 44,
          }}
        />

        <div
          style={{
            fontSize: 168,
            fontWeight: 500,
            letterSpacing: 1,
            color: FEN,
            lineHeight: 1,
          }}
        >
          {wordmark}
        </div>

        <div style={{ width: 110, height: 1, background: REED, margin: "34px 0" }} />

        <div
          style={{
            fontSize: 40,
            fontStyle: "italic",
            fontWeight: 400,
            color: FEN_MIST,
            maxWidth: 900,
            textAlign: "center",
          }}
        >
          {tagline}
        </div>

        <div
          style={{
            position: "absolute",
            bottom: 66,
            fontSize: 22,
            letterSpacing: 8,
            color: QUIET,
            paddingLeft: 8,
          }}
        >
          {press}
        </div>
      </div>
    ),
    { ...size, fonts }
  );
}
