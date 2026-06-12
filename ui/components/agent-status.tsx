"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, Cpu, Wifi, WifiOff, Zap } from "lucide-react";

interface AgentStatusProps {
  name: string;
  model: string;
  status: "online" | "offline" | "busy";
  lastSeen?: string;
  taskCount?: number;
}

export function AgentStatus({ name, model, status, lastSeen, taskCount = 0 }: AgentStatusProps) {
  const statusConfig = {
    online: { icon: Wifi, color: "text-green-500", bg: "bg-green-100 dark:bg-green-900/30", badge: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" },
    offline: { icon: WifiOff, color: "text-red-500", bg: "bg-red-100 dark:bg-red-900/30", badge: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" },
    busy: { icon: Zap, color: "text-amber-500", bg: "bg-amber-100 dark:bg-amber-900/30", badge: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm">
            <div className={`rounded-full p-1.5 ${config.bg}`}>
              <Bot className={`h-4 w-4 ${config.color}`} />
            </div>
            {name}
          </CardTitle>
          <Badge className={config.badge}>{status}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Cpu className="h-3.5 w-3.5" />
          <span>{model}</span>
        </div>
        <div className="flex items-center gap-2">
          <Icon className={`h-3.5 w-3.5 ${config.color}`} />
          <span className={config.color}>
            {status === "online" && "Connected"}
            {status === "offline" && "Disconnected"}
            {status === "busy" && `Processing ${taskCount} tasks`}
          </span>
        </div>
        {lastSeen && (
          <p className="text-xs text-muted-foreground">
            Last seen: {new Date(lastSeen).toLocaleString()}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
