import { NextResponse } from "next/server";

export async function GET() {
  const projects = [
    { id: "default", name: "Default Project", slug: "default", specs: 0, adrs: 0, tasks: 0 },
  ];
  return NextResponse.json(projects);
}
