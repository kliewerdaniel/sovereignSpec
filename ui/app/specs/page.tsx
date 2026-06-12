import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function SpecsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Specifications</h1>
          <p className="text-muted-foreground text-sm">
            Browse and manage specification documents
          </p>
        </div>
        <Link href="/specs/new" className={cn(buttonVariants({ variant: "default" }), "gap-1.5")}>
          <Plus className="h-4 w-4" /> New Spec
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">All Specifications</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12 text-muted-foreground">
            <p className="text-sm">
              No specifications yet.{" "}
              <Link href="/specs/new" className="underline underline-offset-2">
                Create your first spec
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
