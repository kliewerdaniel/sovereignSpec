import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    ollama: { host: "http://localhost:11434", model: "qwen2.5-coder:32b" },
    adapter: "generic",
    chromadb: { path: ".sovereignspec/memory/chromadb" },
    watcher: { enabled: true, debounce_ms: 500 },
  });
}

export async function PUT(request: Request) {
  const body = await request.json();
  return NextResponse.json(body);
}
