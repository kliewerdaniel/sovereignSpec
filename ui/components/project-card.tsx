"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FolderGit2, FileText, GitBranch, AlertCircle } from "lucide-react";

interface ProjectCardProps {
  name: string;
  slug: string;
  specCount?: number;
  taskCount?: number;
  driftCount?: number;
  lastModified?: string;
  status?: "active" | "inactive" | "needs_attention";
}

export function ProjectCard({
  name,
  slug,
  specCount = 0,
  taskCount = 0,
  driftCount = 0,
  lastModified,
  status = "inactive",
}: ProjectCardProps) {
  const statusColors: Record<string, string> = {
    active: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    inactive: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
    needs_attention: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  };

  return (
    <Card className="group hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FolderGit2 className="h-4 w-4 text-primary" />
              {name}
            </CardTitle>
            <CardDescription>{slug}</CardDescription>
          </div>
          <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${statusColors[status]}`}>
            {status.replace("_", " ")}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <FileText className="h-3.5 w-3.5" />
            {specCount} specs
          </span>
          <span className="flex items-center gap-1">
            <GitBranch className="h-3.5 w-3.5" />
            {taskCount} tasks
          </span>
          {driftCount > 0 && (
            <span className="flex items-center gap-1 text-destructive">
              <AlertCircle className="h-3.5 w-3.5" />
              {driftCount} drifts
            </span>
          )}
        </div>
        {lastModified && (
          <p className="mt-2 text-xs text-muted-foreground">
            Last modified: {new Date(lastModified).toLocaleDateString()}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
