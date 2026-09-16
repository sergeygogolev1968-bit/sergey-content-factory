import type { Config } from "@netlify/functions";

const ASSETS: Record<string, string> = {
  "slide_01.jpg": "PLACEHOLDER"
};

export default async (req: Request) => {
  if (req.method !== "GET" && req.method !== "HEAD") return new Response("Method Not Allowed", { status: 405 });
  const name = new URL(req.url).searchParams.get("name") || "";
  const b64 = ASSETS[name];
  if (!b64) return new Response("Not Found", { status: 404 });
  const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  return new Response(req.method === "HEAD" ? null : bytes, { status: 200, headers: { "Content-Type": "image/jpeg", "Content-Length": String(bytes.byteLength), "Cache-Control": "public, max-age=31536000, immutable" } });
};

export const config: Config = { path: "/api/carousel-static" };
