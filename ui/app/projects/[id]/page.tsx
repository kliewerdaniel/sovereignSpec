"use client";

import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function ProjectDetailPage() {
  const params = useParams();
  const id = params.id as string;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{id}</h1>
        <p className="text-muted-foreground text-sm">Project details and settings</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-lg">Specifications</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">No specifications in this project.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-lg">ADRs</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">No ADRs recorded.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-lg">Tasks</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">No tasks.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-lg">Agent Activity</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">No recent activity.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
