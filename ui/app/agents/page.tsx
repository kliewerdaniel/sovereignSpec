import { AgentStatus } from "@/components/agent-status";

const SAMPLE_AGENTS = [
  { name: "Ollama LLM", model: "qwen2.5-coder:32b", status: "online" as const, lastSeen: "2026-06-12T10:30:00Z", taskCount: 3 },
  { name: "Claude Code", model: "claude-sonnet-4-20250514", status: "busy" as const, lastSeen: "2026-06-12T10:28:00Z", taskCount: 2 },
  { name: "OpenCode", model: "deepseek-v4-flash-free", status: "offline" as const, lastSeen: "2026-06-11T18:00:00Z", taskCount: 0 },
];

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Agents</h1>
        <p className="text-muted-foreground text-sm">
          Monitor active AI agents and their status
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {SAMPLE_AGENTS.map((agent) => (
          <AgentStatus key={agent.name} {...agent} />
        ))}
      </div>
    </div>
  );
}
