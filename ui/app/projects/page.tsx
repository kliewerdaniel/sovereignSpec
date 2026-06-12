import { ProjectCard } from "@/components/project-card";

const SAMPLE_PROJECTS = [
  { name: "SovereignSpec", slug: "ss01", specCount: 12, taskCount: 8, driftCount: 2, lastModified: "2026-06-12", status: "active" as const },
  { name: "API Gateway", slug: "api-gateway", specCount: 5, taskCount: 3, driftCount: 0, lastModified: "2026-06-10", status: "active" as const },
  { name: "Legacy App", slug: "legacy-app", specCount: 3, taskCount: 0, driftCount: 0, lastModified: "2026-05-01", status: "inactive" as const },
];

export default function ProjectsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Projects</h1>
        <p className="text-muted-foreground text-sm">
          Manage your SovereignSpec projects
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {SAMPLE_PROJECTS.map((project) => (
          <ProjectCard key={project.slug} {...project} />
        ))}
      </div>
    </div>
  );
}
