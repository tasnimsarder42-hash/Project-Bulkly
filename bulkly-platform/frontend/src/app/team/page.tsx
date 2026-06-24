"use client";

import { useState, useEffect } from "react";
import { fetchApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Users,
  Search,
  UserPlus,
  MoreVertical,
  Mail,
  Shield,
  Activity,
  CheckCircle2,
  Clock,
  X,
  Loader2
} from "lucide-react";
import { cn } from "@/lib/utils";

// Matching backend Enum UserRole
const ROLES = [
  { id: "org_admin", label: "Org Admin", color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 border-purple-200" },
  { id: "marketing_manager", label: "Marketing Manager", color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200" },
  { id: "sales_agent", label: "Sales Agent", color: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200" },
  { id: "support_agent", label: "Support Agent", color: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200" },
  { id: "viewer", label: "Viewer", color: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400 border-slate-200" },
];

interface User {
  id: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
  avatar_url?: string;
  created_at: string;
}

export default function TeamPage() {
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("sales_agent");
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [isInviting, setIsInviting] = useState(false);

  useEffect(() => {
    fetchApi<User[]>("/users")
      .then(data => setUsers(data))
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  const filteredUsers = users.filter(u => 
    u.full_name.toLowerCase().includes(search.toLowerCase()) || 
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail) return;
    setIsInviting(true);

    try {
      const newUser = await fetchApi<User>("/users/invite", {
        method: "POST",
        body: JSON.stringify({ email: inviteEmail, role: inviteRole })
      });
      setUsers([newUser, ...users]);
      setInviteEmail("");
      setIsInviteModalOpen(false);
    } catch (err: any) {
      alert(err.message || "Failed to invite user");
    } finally {
      setIsInviting(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between shrink-0">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-foreground">Team & Users</h2>
          <p className="text-muted-foreground mt-1">Manage your organization members, assign roles, and track activity.</p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-2">
          <Button onClick={() => setIsInviteModalOpen(true)} className="gap-2 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary/90 hover:to-indigo-600/90 text-white shadow-md">
            <UserPlus className="h-4 w-4" />
            Invite User
          </Button>
        </div>
      </div>

      {/* Invite Modal Overlay */}
      {isInviteModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
          <Card className="w-full max-w-md shadow-2xl border-primary/20 animate-in zoom-in-95 duration-200">
            <form onSubmit={handleInvite}>
              <CardHeader className="border-b border-border bg-muted/10">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl flex items-center gap-2">
                    <UserPlus className="h-5 w-5 text-primary" />
                    Invite Team Member
                  </CardTitle>
                  <Button type="button" variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsInviteModalOpen(false)}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <CardDescription>Send an email invitation to join your workspace.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-6">
                <div>
                  <label className="text-sm font-semibold text-foreground mb-1 block">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input 
                      type="email" 
                      placeholder="colleague@company.com" 
                      className="pl-9" 
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-semibold text-foreground mb-1 block">Assign Role</label>
                  <div className="grid grid-cols-1 gap-2 mt-2">
                    {ROLES.map(role => (
                      <div 
                        key={role.id}
                        className={cn(
                          "flex items-center gap-3 p-3 rounded-md border cursor-pointer transition-all",
                          inviteRole === role.id ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"
                        )}
                        onClick={() => setInviteRole(role.id)}
                      >
                        <div className={cn("h-4 w-4 rounded-full border flex items-center justify-center shrink-0", inviteRole === role.id ? "border-primary" : "border-muted-foreground")}>
                          {inviteRole === role.id && <div className="h-2 w-2 bg-primary rounded-full" />}
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-foreground">{role.label}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
              <div className="p-4 border-t border-border bg-muted/10 flex justify-end gap-2 rounded-b-xl">
                <Button type="button" variant="outline" onClick={() => setIsInviteModalOpen(false)} disabled={isInviting}>Cancel</Button>
                <Button type="submit" disabled={isInviting}>
                  {isInviting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                  Send Invitation
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Main Content Area */}
      <Card className="flex-1 flex flex-col border-border shadow-sm min-h-0">
        <div className="p-4 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-muted/10 shrink-0">
          <div className="relative w-full sm:max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search users by name or email..." 
              className="pl-9 bg-background" 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Users className="h-4 w-4" />
            <span>{users.length} Total Members</span>
          </div>
        </div>

        <div className="flex-1 overflow-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase bg-muted/30 sticky top-0 z-10 border-b border-border">
              <tr>
                <th className="px-6 py-4 font-semibold">User</th>
                <th className="px-6 py-4 font-semibold">Role</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold">Joined</th>
                <th className="px-6 py-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <Loader2 className="h-6 w-6 animate-spin text-primary mx-auto" />
                  </td>
                </tr>
              ) : filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-muted-foreground">
                    No users found matching your search.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => {
                  const roleDef = ROLES.find(r => r.id === user.role);
                  return (
                    <tr key={user.id} className="bg-card hover:bg-muted/30 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <Avatar className="h-10 w-10 border border-border">
                            <AvatarImage src={user.avatar_url} />
                            <AvatarFallback className={cn("text-xs font-semibold", !user.is_active ? "bg-muted text-muted-foreground" : "bg-primary/10 text-primary")}>
                              {user.full_name.charAt(0).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-semibold text-foreground">{user.full_name}</p>
                            <p className="text-xs text-muted-foreground">{user.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant="outline" className={cn("border", roleDef?.color)}>
                          {roleDef?.label || user.role}
                        </Badge>
                      </td>
                      <td className="px-6 py-4">
                        {user.is_active ? (
                          <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-500 text-xs font-medium">
                            <CheckCircle2 className="h-3.5 w-3.5" /> Active
                          </div>
                        ) : (
                          <div className="flex items-center gap-1.5 text-amber-600 dark:text-amber-500 text-xs font-medium">
                            <Clock className="h-3.5 w-3.5" /> Pending
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-muted-foreground text-xs">
                        {user.created_at ? new Date(user.created_at).toLocaleDateString() : "Unknown"}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
