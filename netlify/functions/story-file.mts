import { getStore } from "@netlify/blobs";
import type { Config } from "@netlify/functions";

function cleanName(value: string) {
  return value.replace(/[^a-zA-Z0-9._-]/g, "_").slice(0, 120);
}

export default async (req: Request) => {
  if (req.method !== "GET" && req.method !== "HEAD") {
    return new Response("Method Not Allowed", { status: 405 });
  }

  const name = cleanName(new URL(req.url).searchParams.get("name") || "");
  if (!name) return new Response("Missing name", { status: 400 });

  const store = getStore("instagram-stories", { consistency: "strong" });
  const data = await store.get(`stories/${name}`, { type: "arrayBuffer" });
  if (!data) return new Response("Not Found", { status: 404 });

  return new Response(req.method === "HEAD" ? null : data, {
    status: 200,
    headers: {
      "Content-Type": "video/mp4",
      "Content-Length": String(data.byteLength),
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
};

export const config: Config = {
  path: "/api/story-file",
};
