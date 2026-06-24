import Link from "next/link";
import { 
  LayoutDashboard, 
  Users, 
  MessageSquare, 
  Megaphone, 
  BarChart, 
  Settings,
  Workflow,
  Shield,
  FormInput,
  Radio,
  UserCog
} from "lucide-react";

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'CRM & Leads', href: '/crm', icon: Users },
  { name: 'Lead Forms', href: '/forms', icon: FormInput },
  { name: 'Communications', href: '/communications', icon: MessageSquare },
  { name: 'Broadcasts', href: '/broadcast', icon: Radio },
  { name: 'Ad Campaigns', href: '/campaigns', icon: Megaphone },
  { name: 'Automation', href: '/automation', icon: Workflow },
  { name: 'Analytics', href: '/analytics', icon: BarChart },
  { name: 'Team & Users', href: '/team', icon: UserCog },
];

export function Sidebar() {
  return (
    <div className="flex h-full w-64 flex-col bg-card border-r border-border">
      <div className="flex h-16 shrink-0 items-center px-6">
        <h1 className="text-xl font-bold tracking-tight text-primary">BULKLY<span className="text-foreground">V2</span></h1>
      </div>
      <nav className="flex flex-1 flex-col px-4 py-4 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-border flex flex-col gap-1">
        <Link href="/admin" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-amber-600 dark:text-amber-500 hover:bg-accent transition-colors">
          <Shield className="h-4 w-4" />
          Admin Panel
        </Link>
        <Link href="/settings" className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
          <Settings className="h-4 w-4" />
          Settings
        </Link>
      </div>
    </div>
  );
}
