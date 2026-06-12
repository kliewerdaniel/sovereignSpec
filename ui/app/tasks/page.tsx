import { TaskBoard } from "@/components/task-board";

const SAMPLE_TASKS = [
  { id: "t1", title: "Implement user auth", status: "in_progress" as const, specId: "spec-1", priority: "high" as const },
  { id: "t2", title: "Add API endpoints", status: "pending" as const, specId: "spec-1", priority: "medium" as const },
  { id: "t3", title: "Write unit tests", status: "completed" as const, specId: "spec-2", priority: "low" as const },
  { id: "t4", title: "Database migration", status: "in_progress" as const, specId: "spec-3", priority: "high" as const },
  { id: "t5", title: "Deploy to staging", status: "pending" as const, specId: "spec-3", priority: "medium" as const },
];

export default function TasksPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Task Board</h1>
        <p className="text-muted-foreground text-sm">
          Track implementation tasks across specifications
        </p>
      </div>

      <TaskBoard tasks={SAMPLE_TASKS} />
    </div>
  );
}
