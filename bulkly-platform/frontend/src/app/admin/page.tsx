"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  ShieldAlert, 
  Activity, 
  Users, 
  Database,
  Server,
  AlertTriangle,
  CheckCircle2,
  Lock,
  MoreHorizontal
} from "lucide-react";

export default function AdminPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">Super Admin Console</h2>
            <Badge variant="destructive" className="h-6 gap-1"><ShieldAlert className="h-3 w-3" /> Restricted</Badge>
          </div>
          <p className="text-muted-foreground mt-1">Platform-wide analytics, user management, and system health.</p>
        </div>
      </div>

      {/* System Health Overview */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-emerald-500/20 bg-emerald-500/5">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-emerald-700 dark:text-emerald-400">System Status</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">All Systems Operational</div>
            <p className="text-xs text-muted-foreground mt-1">Uptime: 99.99% (Last 30 days)</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Organizations</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">1,248</div>
            <p className="text-xs text-emerald-500 mt-1 font-medium">+12 this week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Messages Queued</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">14,205</div>
            <p className="text-xs text-muted-foreground mt-1">Celery workers active: 8</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Database Load</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">34%</div>
            <div className="h-2 w-full bg-muted rounded-full mt-2 overflow-hidden">
              <div className="h-full bg-primary w-[34%]"></div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Organizations Table */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Organizations</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Organization</TableHead>
                  <TableHead>Plan</TableHead>
                  <TableHead>Users</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {[
                  { name: "Acme Corp", plan: "Enterprise", users: 45, status: "Active" },
                  { name: "TechStartup.io", plan: "Professional", users: 12, status: "Active" },
                  { name: "Global Reach Agency", plan: "Business", users: 28, status: "Warning" },
                  { name: "Local Shop", plan: "Starter", users: 2, status: "Suspended" },
                ].map((org, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{org.name}</TableCell>
                    <TableCell><Badge variant="outline">{org.plan}</Badge></TableCell>
                    <TableCell>{org.users}</TableCell>
                    <TableCell>
                      {org.status === 'Active' && <Badge variant="success">Active</Badge>}
                      {org.status === 'Warning' && <Badge variant="warning">Rate Limit Warn</Badge>}
                      {org.status === 'Suspended' && <Badge variant="destructive">Suspended</Badge>}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Security & Compliance Panel */}
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-muted-foreground" />
              Security & Compliance
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col gap-4">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg flex gap-3">
              <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0" />
              <div>
                <h4 className="text-sm font-semibold text-foreground">API Rate Limit Approaching</h4>
                <p className="text-xs text-muted-foreground mt-0.5">Global Reach Agency has hit 90% of their WhatsApp daily sending limit.</p>
              </div>
            </div>
            
            <div className="space-y-4 mt-2">
              <h4 className="text-sm font-semibold border-b border-border pb-2">System Logs</h4>
              <div className="space-y-3">
                {[
                  { event: "Admin login", user: "super@bulkly.com", time: "2m ago" },
                  { event: "Plan upgraded", user: "TechStartup.io", time: "15m ago" },
                  { event: "Webhook failed", user: "System", time: "1h ago", error: true },
                  { event: "DB Backup completed", user: "System", time: "3h ago" },
                ].map((log, i) => (
                  <div key={i} className="flex justify-between items-start">
                    <div>
                      <p className={cn("text-sm", log.error ? "text-destructive font-medium" : "text-foreground")}>{log.event}</p>
                      <p className="text-xs text-muted-foreground">{log.user}</p>
                    </div>
                    <span className="text-xs text-muted-foreground">{log.time}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-auto pt-4">
              <Button variant="outline" className="w-full gap-2">
                <Server className="h-4 w-4" />
                View Full Audit Logs
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
