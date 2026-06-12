"use client";

import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function SpecDetailPage() {
  const params = useParams();
  const id = params.id as string;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{id}</h1>
          <div className="flex items-center gap-2 mt-1">
            <Badge variant="outline">draft</Badge>
            <span className="text-sm text-muted-foreground">v1.0.0</span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Edit</Button>
          <Button>Validate</Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader><CardTitle className="text-lg">Purpose</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">No purpose defined.</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-lg">Requirements</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">No requirements defined.</p>
            </CardContent>
          </Card>
        </div>
        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle className="text-lg">Related</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">No related items.</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-lg">Tasks</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">No tasks.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
