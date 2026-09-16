import { getStore } from "@netlify/blobs";
import type { Config } from "@netlify/functions";

const STORE = "instagram-carousel";

function cleanName(value: string) {
  return value.replace(/[^a-zA-Z0-9._-]/g, "_").slice(0, 120);
}

export default async (req: Request) => {
  if (req.method !== "GET") return new Response("Method Not Allowed", { status: 405 });
  const url = new URL(req.url);
  const name = cleanName(url.searchParams.get("name") || "");
  if (!name) return new Response("Missing name", { status: 400 });

  const store = getStore(STORE, { consistency: "strong" });
  const entry = await store.getWithMetadata(`assets/${name}`, { type: "arrayBuffer" });
  if (!entry?.data) return new Response("Not Found", { status: 404 });

  const contentType = typeof entry.metadata?.contentType === "string" ? entry.metadata.contentType : "image/jpeg";
  return new Response(entry.data, {
    status: 200,
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
};

export const config: Config = { path: "/api/carousel-file" };
