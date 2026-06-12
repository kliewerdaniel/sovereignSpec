"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function NewSpecPage() {
  const [yaml, setYaml] = useState(`id: my-spec
title: My Specification
version: 1.0.0
status: draft
purpose: |
  Describe the purpose of this specification
requirements:
  - System must ...
constraints:
  - ...
acceptance_criteria:
  - ...
`);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">New Specification</h1>
        <p className="text-muted-foreground text-sm">
          Create a new .sspec specification document
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Specification YAML</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="yaml">YAML Content</Label>
              <Textarea
                id="yaml"
                className="min-h-[400px] font-mono text-sm"
                value={yaml}
                onChange={(e) => setYaml(e.target.value)}
              />
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline">Validate</Button>
              <Button>Save Specification</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
