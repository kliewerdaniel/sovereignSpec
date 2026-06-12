"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground text-sm">
          Configure Ollama models, agent adapters, and system preferences
        </p>
      </div>

      <div className="grid gap-6 max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Ollama Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="host">Host</Label>
              <Input id="host" defaultValue="http://localhost:11434" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gen-model">Generation Model</Label>
              <Select defaultValue="qwen2.5-coder:32b">
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="qwen2.5-coder:32b">qwen2.5-coder:32b</SelectItem>
                  <SelectItem value="llama3.1:70b">llama3.1:70b</SelectItem>
                  <SelectItem value="codestral:latest">codestral:latest</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Agent Adapter</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="adapter">Adapter</Label>
              <Select defaultValue="generic">
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="generic">Generic</SelectItem>
                  <SelectItem value="claude-code">Claude Code</SelectItem>
                  <SelectItem value="opencode">OpenCode</SelectItem>
                  <SelectItem value="cursor">Cursor</SelectItem>
                  <SelectItem value="cline">Cline</SelectItem>
                  <SelectItem value="roocode">RooCode</SelectItem>
                  <SelectItem value="codex">Codex CLI</SelectItem>
                  <SelectItem value="aider">Aider</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">Ollama: Checking...</Badge>
              <Badge variant="outline">ChromaDB: Checking...</Badge>
              <Badge variant="outline">SQLite: Available</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
