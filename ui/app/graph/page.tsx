"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function GraphPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Knowledge Graph</h1>
        <p className="text-muted-foreground text-sm">
          Visualize relationships between specifications, modules, and ADRs
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Graph Explorer</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-24 text-muted-foreground border-2 border-dashed rounded-lg">
            <div className="text-center space-y-2">
              <p className="text-sm font-medium">No graph data</p>
              <p className="text-xs">
                Create specifications to populate the knowledge graph
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
