"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Play, 
  MessageSquare, 
  Mail, 
  GitBranch, 
  Clock, 
  Users, 
  Plus, 
  Settings,
  MoreVertical,
  CheckCircle2,
  Save,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";

// Vertical Node Builder Concept
type NodeType = "trigger" | "action" | "condition" | "delay";

interface WorkflowNode {
  id: string;
  type: NodeType;
  title: string;
  description: string;
  icon: React.ReactNode;
  status: "active" | "draft";
}

const mockWorkflow: WorkflowNode[] = [
  {
    id: "node-1",
    type: "trigger",
    title: "Lead Generated",
    description: "Source: Meta Ads (Campaign: Q3 Retargeting)",
    icon: <Users className="h-5 w-5 text-purple-500" />,
    status: "active",
  },
  {
    id: "node-2",
    type: "action",
    title: "AI Lead Qualification",
    description: "Agent: Sales Rep bot analyzing lead intent.",
    icon: <Zap className="h-5 w-5 text-amber-500" />,
    status: "active",
  },
  {
    id: "node-3",
    type: "condition",
    title: "If Lead Score > 80",
    description: "True branch follows",
    icon: <GitBranch className="h-5 w-5 text-blue-500" />,
    status: "active",
  },
  {
    id: "node-4",
    type: "action",
    title: "Send WhatsApp Message",
    description: "Template: 'High-Intent Welcome'",
    icon: <MessageSquare className="h-5 w-5 text-emerald-500" />,
    status: "active",
  },
  {
    id: "node-5",
    type: "delay",
    title: "Wait 2 Days",
    description: "If no reply received",
    icon: <Clock className="h-5 w-5 text-slate-500" />,
    status: "active",
  },
  {
    id: "node-6",
    type: "action",
    title: "Send Follow-up Email",
    description: "Template: 'Checking In'",
    icon: <Mail className="h-5 w-5 text-rose-500" />,
    status: "draft",
  }
];

export default function AutomationPage() {
  const [selectedNode, setSelectedNode] = useState<string | null>("node-4");

  return (
    <div className="flex flex-col gap-6 h-[calc(100vh-6rem)]">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between shrink-0">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">Hot Lead Conversion</h2>
            <Badge variant="success" className="h-6">Active</Badge>
          </div>
          <p className="text-muted-foreground mt-1">Visual workflow builder for marketing automation.</p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-2">
          <Button variant="outline" className="gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Test Workflow
          </Button>
          <Button className="gap-2">
            <Save className="h-4 w-4" />
            Publish Changes
          </Button>
        </div>
      </div>

      <div className="flex-1 bg-card rounded-xl border border-border shadow-sm flex overflow-hidden">
        {/* Left Pane - Canvas */}
        <div className="flex-1 overflow-y-auto bg-muted/20 relative p-8 flex flex-col items-center">
          
          <div className="absolute top-4 left-4 flex gap-2">
            <Badge variant="outline" className="bg-background">Triggers: 1</Badge>
            <Badge variant="outline" className="bg-background">Actions: 3</Badge>
          </div>

          {/* Workflow Builder */}
          <div className="w-full max-w-md relative pb-20">
            {mockWorkflow.map((node, index) => (
              <div key={node.id} className="relative flex flex-col items-center">
                
                {/* Connection Line from previous */}
                {index > 0 && (
                  <div className="h-8 w-[2px] bg-border my-1"></div>
                )}

                {/* Node Card */}
                <div 
                  onClick={() => setSelectedNode(node.id)}
                  className={cn(
                    "w-full bg-background border-2 rounded-xl p-4 cursor-pointer transition-all hover:shadow-md hover:border-primary/50 flex items-center gap-4 group relative",
                    selectedNode === node.id ? "border-primary shadow-sm" : "border-border",
                    node.type === "trigger" ? "shadow-[0_0_15px_-3px_rgba(168,85,247,0.3)]" : ""
                  )}
                >
                  <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center shrink-0">
                    {node.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-sm truncate pr-2">{node.title}</h4>
                      {node.status === 'draft' && <span className="text-[10px] uppercase font-bold text-amber-500 bg-amber-500/10 px-1.5 py-0.5 rounded-sm">Draft</span>}
                    </div>
                    <p className="text-xs text-muted-foreground truncate mt-0.5">{node.description}</p>
                  </div>
                  <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreVertical className="h-4 w-4 text-muted-foreground" />
                  </Button>
                </div>

                {/* Insert Node Button */}
                <div className="absolute -bottom-5 z-10 opacity-0 hover:opacity-100 transition-opacity">
                  <Button size="icon" className="h-6 w-6 rounded-full shadow-sm bg-background border border-border text-foreground hover:bg-primary hover:text-primary-foreground hover:border-primary">
                    <Plus className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
            
            {/* End of Workflow */}
            <div className="h-8 w-[2px] bg-border my-1 mx-auto"></div>
            <div className="w-12 h-12 rounded-full border-2 border-dashed border-border flex items-center justify-center mx-auto text-muted-foreground bg-background">
              <Play className="h-4 w-4" />
            </div>

          </div>
        </div>

        {/* Right Pane - Configuration Drawer */}
        <div className="w-96 border-l border-border bg-background flex flex-col">
          {selectedNode ? (
            <>
              <div className="p-4 border-b border-border flex items-center gap-3 bg-muted/10">
                <div className="h-8 w-8 rounded-md bg-emerald-500/10 flex items-center justify-center shrink-0">
                  <MessageSquare className="h-4 w-4 text-emerald-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-sm">Send WhatsApp Message</h3>
                  <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Action Node</p>
                </div>
              </div>
              
              <div className="flex-1 p-6 overflow-y-auto space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Node Name</label>
                  <input type="text" className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none" defaultValue="Send WhatsApp Message" />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Message Template</label>
                  <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none">
                    <option>High-Intent Welcome</option>
                    <option>Abandoned Cart Reminder</option>
                    <option>Custom AI Prompt</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium flex justify-between">
                    Message Preview
                    <span className="text-xs text-primary cursor-pointer hover:underline">Edit Template</span>
                  </label>
                  <div className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/20 text-sm">
                    <p className="text-foreground">Hi {"{lead.name}"}, saw you were checking out our new package. Do you have any questions I can answer right now?</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-border">
                  <Button variant="outline" className="w-full gap-2 text-destructive hover:text-destructive hover:bg-destructive/10 border-destructive/20">
                    Delete Node
                  </Button>
                </div>
              </div>
              
              <div className="p-4 border-t border-border bg-muted/10">
                <Button className="w-full">Save Configuration</Button>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground p-6 text-center">
              <div>
                <Settings className="h-12 w-12 mx-auto mb-4 opacity-20" />
                <p className="font-medium text-foreground">No Node Selected</p>
                <p className="text-sm mt-1">Select a node from the canvas to configure its settings.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
