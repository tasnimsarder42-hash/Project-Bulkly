"use client";

import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { TopNav } from "@/components/TopNav";
import { AICopilot } from "@/components/AICopilot";

export function LayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAuthPage = pathname?.startsWith("/login") || pathname?.startsWith("/register");

  if (isAuthPage) {
    return <main className="flex-1 overflow-y-auto">{children}</main>;
  }

  return (
    <>
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 z-50">
        <Sidebar />
      </div>
      <div className="flex flex-col flex-1 lg:pl-64 h-full relative">
        <TopNav />
        <main className="flex-1 overflow-y-auto bg-muted/30 pb-20">
          <div className="mx-auto max-w-7xl p-4 sm:p-6 lg:p-8 h-full">
            {children}
          </div>
        </main>
        <AICopilot />
      </div>
    </>
  );
}
