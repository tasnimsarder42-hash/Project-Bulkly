"use client";

import { useState, useEffect } from "react";
import { fetchApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Send,
  Users,
  MessageSquare,
  CheckCircle2,
  Filter,
  ArrowRight,
  ArrowLeft,
  Smartphone,
  Mail,
  Zap,
  Sparkles,
  Loader2
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Template {
  id: string;
  name: string;
  channel: string;
  content: string;
}

export default function BroadcastPage() {
  const [step, setStep] = useState(1);
  const [channel, setChannel] = useState("whatsapp");
  const [audienceFilter, setAudienceFilter] = useState("all");
  const [templateId, setTemplateId] = useState("");
  const [message, setMessage] = useState("");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [sendResult, setSendResult] = useState<{success: boolean, count: number}|null>(null);

  // Fetch templates on load
  useEffect(() => {
    fetchApi<Template[]>("/messaging/templates")
      .then(data => setTemplates(data))
      .catch(e => console.error(e));
  }, []);

  const handleFireBroadcast = async () => {
    setIsSending(true);
    try {
      const res = await fetchApi<{success: boolean, messages_sent: number}>("/messaging/broadcast", {
        method: "POST",
        body: JSON.stringify({
          channel,
          audience_filter: audienceFilter,
          message
        })
      });
      setSendResult({ success: res.success, count: res.messages_sent });
    } catch (e) {
      console.error(e);
      setSendResult({ success: false, count: 0 });
    } finally {
      setIsSending(false);
    }
  };
  
  // Mock calculations
  const audienceCount = audienceFilter === "all" ? 1240 : audienceFilter === "hot" ? 350 : 890;
  const estimatedCost = channel === "whatsapp" ? (audienceCount * 0.015).toFixed(2) : "0.00";

  return (
    <div className="flex flex-col gap-6 h-full pb-10 max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between shrink-0">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-foreground">Bulk Messaging Engine</h2>
          <p className="text-muted-foreground mt-1">Select your audience, craft your message, and broadcast across channels.</p>
        </div>
      </div>

      {/* Stepper */}
      <div className="flex items-center justify-between relative mb-4">
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-0.5 bg-border -z-10" />
        {[
          { num: 1, title: "Audience", icon: Users },
          { num: 2, title: "Message", icon: MessageSquare },
          { num: 3, title: "Review", icon: CheckCircle2 }
        ].map((s) => (
          <div key={s.num} className="flex flex-col items-center gap-2 bg-background px-4">
            <div className={cn(
              "h-10 w-10 rounded-full flex items-center justify-center border-2 font-bold transition-colors",
              step >= s.num ? "bg-primary border-primary text-primary-foreground" : "bg-card border-muted-foreground/30 text-muted-foreground"
            )}>
              <s.icon className="h-5 w-5" />
            </div>
            <span className={cn("text-xs font-semibold uppercase tracking-wider", step >= s.num ? "text-primary" : "text-muted-foreground")}>
              {s.title}
            </span>
          </div>
        ))}
      </div>

      {/* Wizard Content */}
      <Card className="border-primary/20 shadow-lg relative overflow-hidden min-h-[400px] flex flex-col">
        {step === 1 && (
          <>
            <CardHeader>
              <CardTitle>1. Select Audience</CardTitle>
              <CardDescription>Choose the channel and filter the CRM leads you want to target.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 flex-1">
              <div>
                <label className="text-sm font-semibold text-foreground mb-3 block">Messaging Channel</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {[
                    { id: "whatsapp", label: "WhatsApp", icon: Smartphone, color: "text-emerald-500" },
                    { id: "sms", label: "SMS", icon: MessageSquare, color: "text-blue-500" },
                    { id: "email", label: "Email", icon: Mail, color: "text-amber-500" }
                  ].map((ch) => (
                    <Button 
                      key={ch.id}
                      variant="outline" 
                      className={cn(
                        "h-16 justify-start gap-3 border-2 transition-all",
                        channel === ch.id ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                      )}
                      onClick={() => setChannel(ch.id)}
                    >
                      <ch.icon className={cn("h-6 w-6 shrink-0", channel === ch.id ? ch.color : "text-muted-foreground")} />
                      <div className="text-left">
                        <div className={cn("font-semibold", channel === ch.id ? "text-foreground" : "text-muted-foreground")}>{ch.label}</div>
                      </div>
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold text-foreground mb-3 block">Target Segment</label>
                <div className="space-y-3">
                  {[
                    { id: "all", label: "All Active Leads", desc: "Every lead with valid contact info." },
                    { id: "hot", label: "Hot Leads Only", desc: "Leads with a CRM score > 80." },
                    { id: "cold", label: "Re-engagement Segment", desc: "Leads not contacted in 30 days." }
                  ].map((seg) => (
                    <div 
                      key={seg.id}
                      className={cn(
                        "flex items-start gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all",
                        audienceFilter === seg.id ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 bg-card"
                      )}
                      onClick={() => setAudienceFilter(seg.id)}
                    >
                      <div className={cn(
                        "mt-0.5 h-4 w-4 rounded-full border-2 flex items-center justify-center shrink-0",
                        audienceFilter === seg.id ? "border-primary" : "border-muted-foreground"
                      )}>
                        {audienceFilter === seg.id && <div className="h-2 w-2 bg-primary rounded-full" />}
                      </div>
                      <div>
                        <p className="font-semibold text-sm text-foreground">{seg.label}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">{seg.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-muted/30 p-4 rounded-lg border border-border flex items-center justify-between mt-4">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Estimated Audience Size:</span>
                </div>
                <span className="text-xl font-bold text-primary">{audienceCount} Leads</span>
              </div>
            </CardContent>
          </>
        )}

        {step === 2 && (
          <>
            <CardHeader>
              <CardTitle>2. Compose Message</CardTitle>
              <CardDescription>Select a pre-approved template or draft a custom message.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 flex-1">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="text-sm font-semibold text-foreground">Template Selection</label>
                  <Badge variant="outline" className="text-[10px] uppercase">{channel} templates</Badge>
                </div>
                <div className="flex gap-2 overflow-x-auto pb-2 hide-scrollbar">
                  <Button 
                    variant="outline" 
                    className={cn("shrink-0", !templateId && "border-primary bg-primary/5")}
                    onClick={() => { setTemplateId(""); setMessage(""); }}
                  >
                    Custom Draft
                  </Button>
                  {templates.filter(t => t.channel === channel).map((t) => (
                    <Button 
                      key={t.id}
                      variant="outline" 
                      className={cn("shrink-0", templateId === t.id && "border-primary bg-primary/5")}
                      onClick={() => {
                        setTemplateId(t.id);
                        setMessage(t.content);
                      }}
                    >
                      {t.name}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="text-sm font-semibold text-foreground">Message Content</label>
                  <Button variant="ghost" size="sm" className="h-6 text-xs gap-1 text-primary hover:bg-primary/10">
                    <Sparkles className="h-3 w-3" /> AI Improve
                  </Button>
                </div>
                <div className="relative">
                  <textarea 
                    className="w-full min-h-[200px] p-4 bg-muted/20 border-2 border-border rounded-lg focus:outline-none focus:ring-0 focus:border-primary resize-none"
                    placeholder="Type your message here. Use {{first_name}} to personalize..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                  />
                  <div className="absolute bottom-3 left-3 flex gap-2">
                    <Badge variant="secondary" className="cursor-pointer hover:bg-secondary/80" onClick={() => setMessage(prev => prev + " {{first_name}}")}>{"{{first_name}}"}</Badge>
                    <Badge variant="secondary" className="cursor-pointer hover:bg-secondary/80" onClick={() => setMessage(prev => prev + " {{company}}")}>{"{{company}}"}</Badge>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  <span className={message.length > 1024 ? "text-destructive" : ""}>{message.length}</span> / 1024 characters
                </p>
              </div>
            </CardContent>
          </>
        )}

        {step === 3 && (
          <>
            <CardHeader>
              <CardTitle>3. Review & Broadcast</CardTitle>
              <CardDescription>Final check before sending messages to your leads.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 flex-1">
              
              {sendResult ? (
                <div className="flex flex-col items-center justify-center py-10 text-center animate-in fade-in zoom-in-95">
                  <div className="h-16 w-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mb-4">
                    <CheckCircle2 className="h-8 w-8 text-emerald-600 dark:text-emerald-500" />
                  </div>
                  <h3 className="text-2xl font-bold text-foreground mb-2">Broadcast Sent!</h3>
                  <p className="text-muted-foreground">Successfully queued {sendResult.count} messages via {channel}.</p>
                  <Button className="mt-6" onClick={() => { setStep(1); setSendResult(null); setMessage(""); }}>Start New Broadcast</Button>
                </div>
              ) : (
                <>
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl border border-border bg-card">
                      <p className="text-sm text-muted-foreground mb-1">Target Audience</p>
                      <div className="flex items-end gap-2">
                        <span className="text-3xl font-bold text-foreground">{audienceCount}</span>
                        <span className="text-sm text-muted-foreground mb-1 font-medium">Leads</span>
                      </div>
                      <Badge variant="secondary" className="mt-2 capitalize">{audienceFilter} Segment</Badge>
                    </div>
                    
                    <div className="p-4 rounded-xl border border-border bg-card">
                      <p className="text-sm text-muted-foreground mb-1">Channel & Cost</p>
                      <div className="flex items-end gap-2">
                        <span className="text-3xl font-bold text-foreground">${estimatedCost}</span>
                        <span className="text-sm text-muted-foreground mb-1 font-medium">Estimated</span>
                      </div>
                      <Badge variant="outline" className="mt-2 capitalize flex w-fit gap-1 items-center border-primary/50 text-primary bg-primary/5">
                        <Zap className="h-3 w-3" />
                        {channel} API
                      </Badge>
                    </div>
                  </div>

                  <div className="bg-muted/10 border border-border rounded-xl p-4">
                    <p className="text-sm font-semibold text-foreground mb-2">Message Preview (Alex Johnson)</p>
                    <div className="bg-card p-4 rounded-lg shadow-sm text-sm whitespace-pre-wrap border border-border">
                      {message ? message.replace("{{first_name}}", "Alex").replace("{{company}}", "Acme Corp") : <span className="text-muted-foreground italic">No message content.</span>}
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </>
        )}

        <CardFooter className="border-t border-border bg-muted/10 p-4 shrink-0 flex justify-between">
          {!sendResult && (
            <>
              <Button 
                variant="outline" 
                onClick={() => setStep(prev => prev - 1)} 
                disabled={step === 1 || isSending}
                className="gap-2"
              >
                <ArrowLeft className="h-4 w-4" /> Back
              </Button>
              
              {step < 3 ? (
                <Button onClick={() => setStep(prev => prev + 1)} className="gap-2" disabled={step === 2 && !message.trim()}>
                  Continue <ArrowRight className="h-4 w-4" />
                </Button>
              ) : (
                <Button 
                  className="gap-2 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white shadow-md"
                  onClick={handleFireBroadcast}
                  disabled={isSending}
                >
                  {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  {isSending ? "Sending..." : "Fire Broadcast"}
                </Button>
              )}
            </>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
