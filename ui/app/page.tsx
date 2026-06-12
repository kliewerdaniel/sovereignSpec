import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Plus, FileText, GitFork, CheckSquare, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

const stats = [
  { label: "Specifications", value: "0", icon: FileText, href: "/specs" },
  { label: "Graph Nodes", value: "0", icon: GitFork, href: "/graph" },
  { label: "Tasks", value: "0", icon: CheckSquare, href: "/tasks" },
  { label: "Issues", value: "0", icon: AlertTriangle, href: "/specs", variant: "destructive" as const },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground text-sm">
            SovereignSpec project overview
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/specs/new" className={cn(buttonVariants({ variant: "default" }), "gap-1.5")}>
            <Plus className="h-4 w-4" /> New Spec
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <Card key={s.label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">{s.label}</CardTitle>
              <s.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{s.value}</div>
              <Link href={s.href} className="text-sm underline underline-offset-2">
                View all
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              No recent activity. Create your first specification to get started.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Spec Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Badge variant="outline">0 passing</Badge>
              <Badge variant="destructive">0 failing</Badge>
              <Badge variant="secondary">0 unvalidated</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
