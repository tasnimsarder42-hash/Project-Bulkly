"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  BarChart, 
  PieChart, 
  Download, 
  Calendar as CalendarIcon,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Loader2
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface DashboardData {
  total_revenue: number;
  revenue_this_month: number;
  conversion_rate: number;
  avg_lead_score: number;
  leads_by_status: Record<string, number>;
  leads_by_source: Record<string, number>;
  total_leads: number;
  revenue_trend: { date: string; value: number }[];
}

export default function AnalyticsPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const stats = await fetchApi<DashboardData>("/analytics/dashboard");
        setData(stats);
      } catch (e) {
        console.error("Failed to load analytics", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !data) {
    return (
      <div className="flex h-[80vh] items-center justify-center flex-col gap-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <p className="text-muted-foreground font-medium">Crunching your numbers...</p>
      </div>
    );
  }

  // Helper to format currency
  const formatMoney = (amount: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-foreground">Analytics Center</h2>
          <p className="text-muted-foreground mt-1">Real-time performance metrics and revenue tracking.</p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-2">
          <Button variant="outline" className="gap-2">
            <CalendarIcon className="h-4 w-4" />
            Last 30 Days
          </Button>
          <Button variant="secondary" className="gap-2">
            <Download className="h-4 w-4" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Top Level Metrics */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{formatMoney(data.total_revenue)}</div>
            <p className="text-xs text-emerald-500 flex items-center mt-1 font-medium">
              <TrendingUp className="h-3 w-3 mr-1" /> +20.1% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Monthly Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{formatMoney(data.revenue_this_month)}</div>
            <p className="text-xs text-emerald-500 flex items-center mt-1 font-medium">
              <TrendingDown className="h-3 w-3 mr-1" /> -5.2% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Lead Conversion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{data.conversion_rate}%</div>
            <p className="text-xs text-emerald-500 flex items-center mt-1 font-medium">
              <TrendingUp className="h-3 w-3 mr-1" /> +2.4% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Average Lead Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{data.avg_lead_score}</div>
            <p className="text-xs text-destructive flex items-center mt-1 font-medium">
              <TrendingDown className="h-3 w-3 mr-1" /> -0.8% from last month
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        {/* Main Chart Area */}
        <Card className="col-span-4 flex flex-col">
          <CardHeader>
            <CardTitle className="text-foreground flex items-center gap-2">
              <BarChart className="h-5 w-5 text-primary" />
              Revenue vs Spend Over Time
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex items-center justify-center min-h-[300px]">
            {/* CSS Placeholder for Chart using real trend data length */}
            <div className="w-full h-full flex items-end justify-between gap-1 p-4 border-l border-b border-border/50">
              {data.revenue_trend.slice(0, 15).map((trend, i) => {
                const h = Math.max(10, Math.min(100, (trend.value / 500) * 100)); // Normalize mock values
                return (
                  <div key={i} className="w-full flex gap-1 items-end h-full group relative">
                    <div className="w-full bg-primary/40 rounded-t-sm transition-all hover:bg-primary/60" style={{ height: `${h}%` }}></div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Donut Chart / Source Breakdown */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle className="text-foreground flex items-center gap-2">
              <PieChart className="h-5 w-5 text-primary" />
              Lead Generation Sources
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(data.leads_by_source || {}).filter(([_, v]) => v > 0).map(([source, count], i) => {
                const percent = Math.round((count / data.total_leads) * 100) || 0;
                const colors = ["bg-blue-500", "bg-emerald-500", "bg-red-500", "bg-purple-500", "bg-amber-500", "bg-indigo-500"];
                const color = colors[i % colors.length];
                
                return (
                  <div key={source} className="flex items-center gap-4">
                    <div className="w-24 text-sm font-medium capitalize truncate" title={source}>{source.replace('_', ' ')}</div>
                    <div className="flex-1 h-3 bg-muted rounded-full overflow-hidden">
                      <div className={`h-full ${color}`} style={{ width: `${percent}%` }}></div>
                    </div>
                    <div className="w-12 text-right text-sm text-muted-foreground">{percent}%</div>
                  </div>
                );
              })}
              
              {Object.keys(data.leads_by_source || {}).length === 0 && (
                <p className="text-sm text-muted-foreground py-4 text-center">No source data available.</p>
              )}
            </div>
            
            <div className="mt-8 border-t border-border pt-6">
              <h4 className="text-sm font-semibold mb-4">Conversion Funnel</h4>
              <div className="flex flex-col gap-2 relative">
                <div className="absolute left-[11px] top-4 bottom-4 w-0.5 bg-border -z-10"></div>
                <div className="flex items-center gap-4 bg-card">
                  <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center text-[10px] font-bold text-primary">1</div>
                  <div className="flex-1 text-sm">Site Visitors (Est.)</div>
                  <div className="font-medium text-sm">{data.total_leads * 10}</div>
                </div>
                <div className="flex items-center gap-4 bg-card">
                  <div className="h-6 w-6 rounded-full bg-primary/40 flex items-center justify-center text-[10px] font-bold text-primary">2</div>
                  <div className="flex-1 text-sm flex items-center gap-2">Leads Captured <Badge variant="outline" className="text-[10px] py-0 h-4">10.0% conv.</Badge></div>
                  <div className="font-medium text-sm">{data.total_leads}</div>
                </div>
                <div className="flex items-center gap-4 bg-card">
                  <div className="h-6 w-6 rounded-full bg-primary flex items-center justify-center text-[10px] font-bold text-primary-foreground">3</div>
                  <div className="flex-1 text-sm flex items-center gap-2">Customers <Badge variant="outline" className="text-[10px] py-0 h-4 border-emerald-500/50 text-emerald-500 bg-emerald-500/10">{data.conversion_rate}% conv.</Badge></div>
                  <div className="font-medium text-sm text-emerald-500">{data.leads_by_status?.won || 0}</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
