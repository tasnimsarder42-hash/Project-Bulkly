"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchApi } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  Megaphone, 
  Plus, 
  Search, 
  Filter, 
  TrendingUp, 
  DollarSign, 
  MousePointerClick,
  Users,
  Facebook,
  Instagram,
  MonitorPlay
} from "lucide-react";

interface Campaign {
  id: string;
  name: string;
  platform: string;
  status: string;
  budget_daily: number;
  spend_total: number;
  ctr: number;
  leads_generated: number;
  cpl: number;
}

export default function CampaignsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadCampaigns() {
      try {
        const response = await fetchApi<{items: Campaign[]}>("/campaigns");
        setCampaigns(response.items);
      } catch (error) {
        console.error("Failed to load campaigns:", error);
      } finally {
        setIsLoading(false);
      }
    }
    loadCampaigns();
  }, []);

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'Meta': return <div className="flex -space-x-2"><Facebook className="h-4 w-4 text-blue-600 z-10 bg-background rounded-full" /><Instagram className="h-4 w-4 text-pink-600 bg-background rounded-full" /></div>;
      case 'Google': return <MonitorPlay className="h-4 w-4 text-red-500" />;
      case 'TikTok': return <div className="font-bold text-foreground bg-foreground text-background text-[10px] px-1 rounded-sm">TT</div>;
      default: return <Megaphone className="h-4 w-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    if (status === "Active") return <Badge variant="success">Active</Badge>;
    if (status === "Paused") return <Badge variant="secondary">Paused</Badge>;
    return <Badge variant="outline">{status}</Badge>;
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-foreground">Ad Management Center</h2>
          <p className="text-muted-foreground mt-1">Manage and track your multi-channel advertising campaigns.</p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-2">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Create Campaign
          </Button>
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Spend (30d)</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">$5,940.50</div>
            <p className="text-xs text-muted-foreground mt-1">across 4 active campaigns</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Impressions</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">1.2M</div>
            <p className="text-xs text-emerald-500 mt-1 font-medium">+15% from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Average CTR</CardTitle>
            <MousePointerClick className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">3.2%</div>
            <p className="text-xs text-emerald-500 mt-1 font-medium">+0.4% from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Leads</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">555</div>
            <p className="text-xs text-muted-foreground mt-1">Avg CPL: $10.70</p>
          </CardContent>
        </Card>
      </div>

      <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
        <div className="p-4 border-b border-border flex items-center justify-between gap-4">
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search campaigns..."
              className="pl-8 bg-background"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button variant="outline" className="gap-2 shrink-0">
            <Filter className="h-4 w-4" />
            Filter
          </Button>
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow>
                <TableHead>Campaign Name</TableHead>
                <TableHead>Platform</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Budget</TableHead>
                <TableHead>Spend</TableHead>
                <TableHead>CTR</TableHead>
                <TableHead className="text-right">Leads</TableHead>
                <TableHead className="text-right">CPL</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                    Loading campaigns...
                  </TableCell>
                </TableRow>
              ) : campaigns.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                    No campaigns found.
                  </TableCell>
                </TableRow>
              ) : (
                campaigns.map((campaign) => (
                  <TableRow key={campaign.id}>
                    <TableCell className="font-medium text-foreground">{campaign.name}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getPlatformIcon(campaign.platform)}
                        <span className="text-sm">{campaign.platform}</span>
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(campaign.status)}</TableCell>
                    <TableCell className="text-muted-foreground">${campaign.budget_daily?.toFixed(2)}/day</TableCell>
                    <TableCell>${campaign.spend_total?.toFixed(2) || '0.00'}</TableCell>
                    <TableCell>{campaign.ctr || '0'}%</TableCell>
                    <TableCell className="text-right font-medium text-foreground">{campaign.leads_generated || 0}</TableCell>
                    <TableCell className="text-right text-emerald-500 font-medium">${campaign.cpl?.toFixed(2) || '0.00'}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
