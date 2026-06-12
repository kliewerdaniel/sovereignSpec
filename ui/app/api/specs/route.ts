import { NextResponse } from "next/server";

export async function GET() {
  const specs: unknown[] = [];
  return NextResponse.json(specs);
}

export async function POST(request: Request) {
  const body = await request.json();
  return NextResponse.json({ id: body.id || "new-spec", ...body }, { status: 201 });
}
