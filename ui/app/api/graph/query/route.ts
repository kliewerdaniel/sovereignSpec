import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const breaks = searchParams.get("what-breaks");
  const module = searchParams.get("affects-module");
  return NextResponse.json({ impacted: [], depth: 3 });
}
