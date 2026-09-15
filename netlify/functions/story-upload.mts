import { getStore } from "@netlify/blobs";
import type { Config } from "@netlify/functions";

const STORE = "instagram-stories";
const MAX_CHUNK = 4 * 1024 * 1024;

function authorized(req: Request) {
  const token = req.headers.get("x-upload-token");
  return Boolean(token) && token === Netlify.env.get("STORY_UPLOAD_TOKEN");
}

function cleanName(value: string) {
  return value.replace(/[^a-zA-Z0-9._-]/g, "_").slice(0, 120);
}

export default async (req: Request) => {
  if (!authorized(req)) return new Response("Unauthorized", { status: 401 });
  if (req.method !== "POST") return new Response("Method Not Allowed", { status: 405 });

  const action = req.headers.get("x-upload-action") || "chunk";
  const name = cleanName(req.headers.get("x-story-name") || "story.mp4");
  const store = getStore(STORE, { consistency: "strong" });

  if (action === "chunk") {
    const index = Number(req.headers.get("x-chunk-index"));
    const total = Number(req.headers.get("x-total-chunks"));
    if (!Number.isInteger(index) || !Number.isInteger(total) || index < 0 || index >= total) {
      return new Response("Invalid chunk headers", { status: 400 });
    }

    const data = await req.arrayBuffer();
    if (data.byteLength > MAX_CHUNK) return new Response("Chunk too large", { status: 413 });

    await store.set(`uploads/${name}/${index}.part`, data);
    return Response.json({ ok: true, index, total });
  }

  if (action === "finalize") {
    const total = Number(req.headers.get("x-total-chunks"));
    if (!Number.isInteger(total) || total < 1 || total > 1000) {
      return new Response("Invalid total chunks", { status: 400 });
    }

    const parts: ArrayBuffer[] = [];
    let totalBytes = 0;
    for (let i = 0; i < total; i++) {
      const part = await store.get(`uploads/${name}/${i}.part`, { type: "arrayBuffer" });
      if (!part) return new Response(`Missing chunk ${i}`, { status: 409 });
      parts.push(part);
      totalBytes += part.byteLength;
    }

    const output = new Uint8Array(totalBytes);
    let offset = 0;
    for (const part of parts) {
      output.set(new Uint8Array(part), offset);
      offset += part.byteLength;
    }

    await store.set(`stories/${name}`, output.buffer, { metadata: { contentType: "video/mp4" } });
    for (let i = 0; i < total; i++) await store.delete(`uploads/${name}/${i}.part`);

    return Response.json({
      ok: true,
      url: `/.netlify/functions/story-file?name=${encodeURIComponent(name)}`,
      bytes: totalBytes,
    });
  }

  return new Response("Unknown action", { status: 400 });
};

export const config: Config = {
  path: "/api/story-upload",
};
