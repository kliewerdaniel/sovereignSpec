"use client";

import { useEffect, useRef } from "react";

interface GraphNode {
  id: string;
  type: string;
  label: string;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

interface GraphVisualizationProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

const COLORS: Record<string, string> = {
  SPECIFICATION: "#3b82f6",
  MODULE: "#22c55e",
  ADR: "#a855f7",
  TASK: "#f59e0b",
  AGENT: "#ef4444",
};

export function GraphVisualization({ nodes, edges }: GraphVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || nodes.length === 0) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const positions: Record<string, { x: number; y: number }> = {};
    nodes.forEach((n, i) => {
      const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
      const cx = w / 2;
      const cy = h / 2;
      const r = Math.min(w, h) * 0.3;
      positions[n.id] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
    });

    edges.forEach((e) => {
      const src = positions[e.source];
      const tgt = positions[e.target];
      if (!src || !tgt) return;
      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(tgt.x, tgt.y);
      ctx.strokeStyle = "#666";
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    nodes.forEach((n) => {
      const pos = positions[n.id];
      if (!pos) return;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 8, 0, 2 * Math.PI);
      ctx.fillStyle = COLORS[n.type] || "#888";
      ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.font = "10px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(n.label, pos.x, pos.y + 20);
    });
  }, [nodes, edges]);

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground border-2 border-dashed rounded-lg">
        <p className="text-sm">No graph data to visualize</p>
      </div>
    );
  }

  return (
    <canvas
      ref={canvasRef}
      width={600}
      height={400}
      className="w-full max-w-2xl mx-auto"
    />
  );
}
