"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { fetchApi } from "@/lib/api";
import {
  Search,
  MoreVertical,
  Paperclip,
  Smile,
  Send,
  Phone,
  Video,
  Bot,
  Sparkles,
  Facebook,
  Instagram,
  MessageCircle,
  Mail,
  Loader2
} from "lucide-react";
import { cn } from "@/lib/utils";

// Mock Conversations
const conversations = [
  {
    id: "1",
    name: "Alex Johnson",
    lastMessage: "Is this still available in black?",
    time: "10:42 AM",
    unread: 2,
    channel: "whatsapp",
    avatar: "AJ",
    active: true,
  },
  {
    id: "2",
    name: "Sarah Williams",
    lastMessage: "Thanks for the information!",
    time: "Yesterday",
    unread: 0,
    channel: "messenger",
    avatar: "SW",
    active: false,
  },
  {
    id: "3",
    name: "Michael Brown",
    lastMessage: "Can we schedule a call?",
    time: "Yesterday",
    unread: 0,
    channel: "instagram",
    avatar: "MB",
    active: false,
  },
  {
    id: "4",
    name: "TechStartup Inc",
    lastMessage: "We've reviewed the proposal...",
    time: "Mon",
    unread: 1,
    channel: "email",
    avatar: "TI",
    active: false,
  },
];

// Mock Chat History for active chat
const chatHistory = [
  { id: 1, sender: "them", text: "Hi, I saw your ad for the new software package.", time: "10:30 AM" },
  { id: 2, sender: "us", text: "Hello Alex! Yes, it's currently on early-bird sale. How can I help you?", time: "10:32 AM" },
  { id: 3, sender: "them", text: "Is this still available in black?", time: "10:42 AM" },
];

export default function CommunicationsPage() {
  const [message, setMessage] = useState("");
  const [aiSuggestion, setAiSuggestion] = useState<string | null>(null);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [liveChatHistory, setLiveChatHistory] = useState(chatHistory);
  const [ws, setWs] = useState<WebSocket | null>(null);
  
  // Find active chat (in real app, this would be state)
  const activeChat = conversations.find(c => c.active);

  // Initialize WebSockets
  useEffect(() => {
    // In a real app, org_id comes from auth context
    const org_id = "demo-org-123"; 
    const token = localStorage.getItem("access_token") || "";
    // Note: Assuming backend runs on 8000 locally
    const socket = new WebSocket(`ws://localhost:8000/api/v1/messaging/ws/${org_id}?token=${token}`);
    
    socket.onopen = () => console.log("WS Connected");
    
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.event === "new_message") {
          const msgData = payload.data;
          setLiveChatHistory(prev => [...prev, {
            id: Date.now(),
            sender: msgData.direction === "inbound" ? "them" : "us",
            text: msgData.content,
            time: new Date(msgData.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }]);
        }
      } catch (e) {
        console.error("WS Parse Error", e);
      }
    };

    setWs(socket);
    return () => socket.close();
  }, []);

  const handleSendMessage = () => {
    if (!message.trim() || !activeChat) return;

    // Send to backend API (simulated here since we don't have lead DB hooked up to this exact demo chat)
    // Normally we'd POST to /api/v1/messaging/send
    
    // Optimistic UI update
    setLiveChatHistory(prev => [...prev, {
      id: Date.now(),
      sender: "us",
      text: message,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
    
    setMessage("");
  };

  useEffect(() => {
    if (!activeChat) return;
    
    async function generateReply() {
      setIsGeneratingAI(true);
      setAiSuggestion(null);
      try {
        // Fallback for demo since we might not have the lead_id in the DB
        const lastMsg = liveChatHistory[liveChatHistory.length - 1];
        if (lastMsg.sender === "us") return; // Don't generate reply to our own message
        
        const response = await fetchApi<{reply: string}>("/ai/reply", {
          method: "POST",
          body: JSON.stringify({
            lead_id: "demo-lead-id", // mock ID
            incoming_message: lastMsg.text,
            channel: activeChat?.channel || "whatsapp"
          }),
        }).catch(() => null); // Ignore errors for demo if lead not found

        if (response?.reply) {
          setAiSuggestion(response.reply);
        } else {
          // Mock response if API fails (e.g. lead not found in DB)
          setTimeout(() => {
            setAiSuggestion(`Yes, we currently have it in stock! Would you like me to set one aside for you, ${activeChat?.name}?`);
          }, 1500);
        }
      } finally {
        setIsGeneratingAI(false);
      }
    }

    generateReply();
  }, [activeChat?.id, liveChatHistory.length]);

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'whatsapp': return <MessageCircle className="h-3 w-3 text-emerald-500" />;
      case 'messenger': return <Facebook className="h-3 w-3 text-blue-500" />;
      case 'instagram': return <Instagram className="h-3 w-3 text-pink-500" />;
      case 'email': return <Mail className="h-3 w-3 text-amber-500" />;
      default: return <MessageCircle className="h-3 w-3" />;
    }
  };

  return (
    <div className="flex flex-col gap-6 h-[calc(100vh-6rem)]">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between shrink-0">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-foreground">Communications Hub</h2>
          <p className="text-muted-foreground mt-1">Manage all multi-channel conversations in one place.</p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-2">
          <Button variant="outline" className="gap-2">
            <Bot className="h-4 w-4" />
            AI Auto-Responder Settings
          </Button>
        </div>
      </div>

      <div className="flex-1 bg-card rounded-xl border border-border shadow-sm flex overflow-hidden">
        {/* Left Pane - Conversation List */}
        <div className="w-80 border-r border-border flex flex-col bg-muted/10">
          <div className="p-4 border-b border-border">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search messages..."
                className="pl-8 bg-background"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {conversations.map((chat) => (
              <div 
                key={chat.id} 
                className={cn(
                  "p-4 border-b border-border flex gap-3 cursor-pointer transition-colors hover:bg-muted/50",
                  chat.active ? "bg-muted" : "bg-transparent"
                )}
              >
                <Avatar className="h-10 w-10">
                  <AvatarFallback className="bg-primary/10 text-primary">{chat.avatar}</AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-baseline mb-1">
                    <h4 className="text-sm font-semibold text-foreground truncate">{chat.name}</h4>
                    <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">{chat.time}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {getChannelIcon(chat.channel)}
                    <p className="text-xs text-muted-foreground truncate flex-1">{chat.lastMessage}</p>
                    {chat.unread > 0 && (
                      <span className="bg-primary text-primary-foreground text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center">
                        {chat.unread}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Pane - Active Chat */}
        <div className="flex-1 flex flex-col bg-background">
          {activeChat ? (
            <>
              {/* Chat Header */}
              <div className="h-16 px-6 border-b border-border flex items-center justify-between bg-card">
                <div className="flex items-center gap-4">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-primary/10 text-primary">{activeChat.avatar}</AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
                      {activeChat.name}
                      <Badge variant="outline" className="text-[10px] uppercase h-5 px-1.5 font-bold">
                        {activeChat.channel}
                      </Badge>
                    </h3>
                    <p className="text-xs text-emerald-500 font-medium">Online</p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" className="text-muted-foreground">
                    <Phone className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="text-muted-foreground">
                    <Video className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="text-muted-foreground">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-muted/5">
                {liveChatHistory.map((msg) => (
                  <div 
                    key={msg.id} 
                    className={cn(
                      "flex max-w-[70%]",
                      msg.sender === "us" ? "ml-auto justify-end" : ""
                    )}
                  >
                    <div 
                      className={cn(
                        "rounded-2xl px-4 py-2.5 text-sm shadow-sm",
                        msg.sender === "us" 
                          ? "bg-primary text-primary-foreground rounded-tr-sm" 
                          : "bg-card border border-border text-foreground rounded-tl-sm"
                      )}
                    >
                      <p>{msg.text}</p>
                      <p className={cn(
                        "text-[10px] mt-1 text-right opacity-70",
                        msg.sender === "us" ? "text-primary-foreground/70" : "text-muted-foreground"
                      )}>
                        {msg.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* AI Suggestion Banner (Phase 5) */}
              <div className="px-6 py-2 bg-primary/5 border-t border-b border-border flex items-center justify-between min-h-[3rem]">
                <div className="flex items-center gap-2 text-sm text-foreground flex-1 pr-4">
                  <Sparkles className={cn("h-4 w-4 text-primary shrink-0", isGeneratingAI && "animate-pulse")} />
                  <span className="font-medium shrink-0">AI Suggestion:</span>
                  {isGeneratingAI ? (
                    <span className="text-muted-foreground flex items-center gap-2">
                      <Loader2 className="h-3 w-3 animate-spin" /> Generating contextual reply...
                    </span>
                  ) : (
                    <span className="text-muted-foreground truncate" title={aiSuggestion || ""}>
                      "{aiSuggestion || "No suggestion available."}"
                    </span>
                  )}
                </div>
                <Button 
                  size="sm" 
                  variant="secondary" 
                  className="h-7 text-xs px-3 shrink-0"
                  disabled={isGeneratingAI || !aiSuggestion}
                  onClick={() => setMessage(aiSuggestion || "")}
                >
                  Use Reply
                </Button>
              </div>

              {/* Input Area */}
              <div className="p-4 bg-card">
                <div className="flex items-end gap-2 bg-muted/50 rounded-xl border border-border p-2 focus-within:ring-1 focus-within:ring-primary focus-within:border-primary transition-all">
                  <Button variant="ghost" size="icon" className="shrink-0 h-9 w-9 text-muted-foreground hover:text-foreground">
                    <Paperclip className="h-5 w-5" />
                  </Button>
                  <textarea 
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    placeholder="Type a message..."
                    className="flex-1 max-h-32 min-h-9 bg-transparent border-0 resize-none focus:outline-none focus:ring-0 p-2 text-sm text-foreground placeholder:text-muted-foreground"
                    rows={1}
                  />
                  <Button variant="ghost" size="icon" className="shrink-0 h-9 w-9 text-muted-foreground hover:text-foreground hidden sm:flex">
                    <Smile className="h-5 w-5" />
                  </Button>
                  <Button size="icon" className="shrink-0 h-9 w-9 rounded-lg" onClick={handleSendMessage}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
              <MessageCircle className="h-16 w-16 mb-4 opacity-20" />
              <p className="text-lg font-medium text-foreground mb-1">No Chat Selected</p>
              <p className="text-sm">Select a conversation from the left to start messaging.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
