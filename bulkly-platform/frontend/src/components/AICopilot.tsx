"use client";

import { useState, useRef, useEffect } from "react";
import { fetchApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, X, Send, Sparkles, User, Loader2, Maximize2, Minimize2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  suggestions?: string[];
}

export function AICopilot() {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hi! I'm Bulkly AI, your sales and marketing copilot. How can I help you today?",
      suggestions: ["Analyze my top leads", "Draft a WhatsApp campaign", "How do I set up automations?"]
    }
  ]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping, isOpen]);

  const handleSend = async (text: string) => {
    if (!text.trim() || isTyping) return;

    const userMsg: Message = { id: Date.now().toString(), role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetchApi<{response: string, suggestions?: string[]}>("/ai/chat", {
        method: "POST",
        body: JSON.stringify({ message: text, context: { currentRoute: window.location.pathname } })
      }).catch(() => null);

      if (response?.response) {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: "assistant",
          content: response.response,
          suggestions: response.suggestions
        }]);
      } else {
        // Fallback for demo
        setTimeout(() => {
          setMessages(prev => [...prev, {
            id: Date.now().toString(),
            role: "assistant",
            content: "I understand! I am currently running in demo mode, but I've noted your request.",
            suggestions: ["Show me analytics", "Close chat"]
          }]);
        }, 1000);
      }
    } finally {
      setIsTyping(false);
    }
  };

  const activeSuggestions = messages[messages.length - 1]?.role === "assistant" 
    ? messages[messages.length - 1].suggestions 
    : [];

  if (!isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-2xl p-0 flex items-center justify-center hover:scale-105 transition-transform z-50 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary/90 hover:to-indigo-600/90"
      >
        <Sparkles className="h-6 w-6 text-white absolute animate-pulse opacity-50" />
        <Bot className="h-7 w-7 text-white relative z-10" />
      </Button>
    );
  }

  return (
    <div 
      className={cn(
        "fixed bottom-6 right-6 z-50 flex flex-col bg-card border border-border shadow-2xl rounded-2xl overflow-hidden transition-all duration-300 ease-in-out",
        isExpanded ? "w-[450px] h-[600px] sm:w-[500px] sm:h-[700px]" : "w-[350px] h-[500px]"
      )}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-primary/10 to-indigo-600/10 px-4 py-3 border-b border-border flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="bg-primary p-1.5 rounded-md">
            <Bot className="h-4 w-4 text-primary-foreground" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground leading-none mb-1">Bulkly AI Copilot</h3>
            <p className="text-[10px] text-emerald-500 font-medium leading-none flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Online
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-foreground" onClick={() => setIsExpanded(!isExpanded)}>
            {isExpanded ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-foreground" onClick={() => setIsOpen(false)}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/20" ref={scrollRef}>
        {messages.map((msg) => (
          <div key={msg.id} className={cn("flex gap-3", msg.role === "user" ? "flex-row-reverse" : "")}>
            <div className={cn(
              "h-8 w-8 rounded-full flex items-center justify-center shrink-0 mt-auto",
              msg.role === "assistant" ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground"
            )}>
              {msg.role === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
            </div>
            <div className={cn(
              "rounded-2xl px-4 py-2.5 text-sm max-w-[80%] shadow-sm",
              msg.role === "assistant" 
                ? "bg-card border border-border text-foreground rounded-bl-sm" 
                : "bg-primary text-primary-foreground rounded-br-sm"
            )}>
              {msg.content}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full flex items-center justify-center shrink-0 mt-auto bg-primary/20 text-primary">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-2xl px-4 py-3 bg-card border border-border rounded-bl-sm shadow-sm flex items-center gap-1">
              <span className="h-1.5 w-1.5 bg-primary rounded-full animate-bounce"></span>
              <span className="h-1.5 w-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.2s]"></span>
              <span className="h-1.5 w-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.4s]"></span>
            </div>
          </div>
        )}
      </div>

      {/* Suggestions */}
      {activeSuggestions && activeSuggestions.length > 0 && !isTyping && (
        <div className="px-4 py-2 flex gap-2 overflow-x-auto shrink-0 bg-background border-t border-border/50 hide-scrollbar">
          {activeSuggestions.map((suggestion, i) => (
            <Button 
              key={i} 
              variant="outline" 
              size="sm" 
              className="rounded-full h-7 text-xs whitespace-nowrap bg-muted/50 hover:bg-primary/10 hover:text-primary hover:border-primary/30"
              onClick={() => handleSend(suggestion)}
            >
              {suggestion}
            </Button>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="p-3 bg-card border-t border-border shrink-0">
        <form 
          className="relative flex items-center" 
          onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
        >
          <Input 
            placeholder="Ask Bulkly AI..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isTyping}
            className="pr-10 rounded-full bg-muted/50 border-transparent focus-visible:ring-1 focus-visible:ring-primary focus-visible:border-primary"
          />
          <Button 
            type="submit" 
            size="icon" 
            disabled={!input.trim() || isTyping}
            className="absolute right-1 h-7 w-7 rounded-full bg-primary hover:bg-primary/90 text-white transition-transform active:scale-95"
          >
            {isTyping ? <Loader2 className="h-3 w-3 animate-spin" /> : <Send className="h-3 w-3 ml-0.5" />}
          </Button>
        </form>
      </div>
    </div>
  );
}
