import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TasksPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Task Board</h1>
        <p className="text-muted-foreground text-sm">
          Track implementation tasks across specifications
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {["pending", "in_progress", "completed"].map((status) => (
          <Card key={status}>
            <CardHeader>
              <CardTitle className="text-sm capitalize">
                {status.replace("_", " ")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">No tasks</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
