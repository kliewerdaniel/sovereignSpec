"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle, Clock } from "lucide-react";

interface Task {
  id: string;
  title: string;
  status: "pending" | "in_progress" | "completed";
  specId: string;
  priority: "low" | "medium" | "high";
}

interface TaskBoardProps {
  tasks?: Task[];
}

const STATUS_COLUMNS = [
  { key: "pending", label: "Pending", icon: Circle },
  { key: "in_progress", label: "In Progress", icon: Clock },
  { key: "completed", label: "Completed", icon: CheckCircle2 },
] as const;

const PRIORITY_COLORS: Record<string, string> = {
  low: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  high: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export function TaskBoard({ tasks = [] }: TaskBoardProps) {
  const [draggedId, setDraggedId] = useState<string | null>(null);

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {STATUS_COLUMNS.map(({ key, label, icon: Icon }) => {
        const columnTasks = tasks.filter((t) => t.status === key);
        return (
          <Card key={key} className="min-h-[200px]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Icon className="h-4 w-4" />
                {label}
                <Badge variant="secondary" className="ml-auto">
                  {columnTasks.length}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {columnTasks.length === 0 && (
                <p className="text-sm text-muted-foreground py-4 text-center">No tasks</p>
              )}
              {columnTasks.map((task) => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={() => setDraggedId(task.id)}
                  onDragEnd={() => setDraggedId(null)}
                  data-dragging={draggedId === task.id || undefined}
                  className="group cursor-grab rounded-lg border bg-card p-3 text-sm shadow-sm transition-colors hover:bg-accent data-[dragging]:opacity-50 data-[dragging]:cursor-grabbing"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium truncate">{task.title}</span>
                    <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${PRIORITY_COLORS[task.priority]}`}>
                      {task.priority}
                    </span>
                  </div>
                  <p className="mt-1 text-[10px] text-muted-foreground">{task.specId}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
