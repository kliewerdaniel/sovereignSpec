"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface SpecEditorProps {
  initialYaml?: string;
  onSave?: (yaml: string) => void;
  readOnly?: boolean;
}

export function SpecEditor({ initialYaml = "", onSave, readOnly = false }: SpecEditorProps) {
  const [yaml, setYaml] = useState(initialYaml);
  const [errors, setErrors] = useState<string[]>([]);

  const handleValidate = () => {
    try {
      const lines = yaml.split("\n").filter((l) => l.trim());
      const newErrors: string[] = [];
      if (!yaml.includes("id:")) newErrors.push("Missing 'id' field");
      if (!yaml.includes("title:")) newErrors.push("Missing 'title' field");
      if (!yaml.includes("purpose:")) newErrors.push("Missing 'purpose' field");
      if (!yaml.includes("requirements:")) newErrors.push("Missing 'requirements' field");
      setErrors(newErrors);
    } catch {
      setErrors(["Failed to parse YAML"]);
    }
  };

  return (
    <div className="space-y-4">
      <Textarea
        className="min-h-[400px] font-mono text-sm"
        value={yaml}
        onChange={(e) => setYaml(e.target.value)}
        readOnly={readOnly}
        placeholder="Enter specification YAML..."
      />
      {errors.length > 0 && (
        <div className="space-y-1">
          {errors.map((err, i) => (
            <p key={i} className="text-sm text-destructive">{err}</p>
          ))}
        </div>
      )}
      {!readOnly && (
        <div className="flex gap-2 justify-end">
          <Button variant="outline" onClick={handleValidate}>Validate</Button>
          <Button onClick={() => onSave?.(yaml)}>Save</Button>
        </div>
      )}
    </div>
  );
}
