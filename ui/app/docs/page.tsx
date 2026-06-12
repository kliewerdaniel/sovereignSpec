import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DocsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Documentation</h1>
        <p className="text-muted-foreground text-sm">
          Browse project documentation
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Documentation Hub</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12 text-muted-foreground">
            <p className="text-sm">No documentation generated yet.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
