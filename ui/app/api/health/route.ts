import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    python: true,
    ollama: false,
    chromadb: false,
    sqlite: true,
  });
}
