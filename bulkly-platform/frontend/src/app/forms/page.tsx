"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Type,
  Mail,
  Phone,
  AlignLeft,
  CheckSquare,
  List,
  Save,
  Code,
  Layout,
  Plus,
  Trash2
} from "lucide-react";
import { cn } from "@/lib/utils";

interface FormField {
  id: string;
  type: string;
  label: string;
  required: boolean;
  placeholder?: string;
}

const FIELD_TYPES = [
  { type: "text", label: "Short Text", icon: Type, defaultPlaceholder: "John Doe" },
  { type: "email", label: "Email Address", icon: Mail, defaultPlaceholder: "john@example.com" },
  { type: "tel", label: "Phone Number", icon: Phone, defaultPlaceholder: "+1 (555) 000-0000" },
  { type: "textarea", label: "Long Text", icon: AlignLeft, defaultPlaceholder: "Enter your message here..." },
  { type: "checkbox", label: "Checkbox", icon: CheckSquare },
  { type: "select", label: "Dropdown", icon: List },
];

export default function FormsPage() {
  const [formName, setFormName] = useState("New Lead Capture Form");
  const [fields, setFields] = useState<FormField[]>([
    { id: "1", type: "text", label: "Full Name", required: true, placeholder: "John Doe" },
    { id: "2", type: "email", label: "Email Address", required: true, placeholder: "john@example.com" }
  ]);
  const [showEmbedCode, setShowEmbedCode] = useState(false);

  const addField = (fieldType: any) => {
    const newField: FormField = {
      id: Date.now().toString(),
      type: fieldType.type,
      label: `New ${fieldType.label}`,
      required: false,
      placeholder: fieldType.defaultPlaceholder
    };
    setFields([...fields, newField]);
  };

  const removeField = (id: string) => {
    setFields(fields.filter(f => f.id !== id));
  };

  const generateEmbedCode = () => {
    return `<script src="https://api.bulkly.app/forms/v1/embed.js"></script>\n<div class="bulkly-form-widget" data-form-id="mock-form-${Date.now()}"></div>`;
  };

  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between shrink-0">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-foreground">Lead Generation Forms</h2>
          <p className="text-muted-foreground mt-1">Design forms and embed them on your website to capture inbound leads.</p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-2">
          <Button variant="outline" className="gap-2" onClick={() => setShowEmbedCode(true)}>
            <Code className="h-4 w-4" />
            Get Embed Code
          </Button>
          <Button className="gap-2">
            <Save className="h-4 w-4" />
            Save Form
          </Button>
        </div>
      </div>

      {showEmbedCode && (
        <Card className="border-primary/50 bg-primary/5 mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Embed Code</CardTitle>
            <CardDescription>Copy and paste this snippet into your website's HTML where you want the form to appear.</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="bg-card border border-border p-4 rounded-md text-sm text-muted-foreground overflow-x-auto select-all">
              {generateEmbedCode()}
            </pre>
            <div className="mt-4 flex justify-end">
              <Button variant="outline" size="sm" onClick={() => setShowEmbedCode(false)}>Close</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
        
        {/* Left Column: Form Builder Toolbox */}
        <Card className="lg:col-span-4 flex flex-col h-[600px] lg:h-auto">
          <CardHeader className="border-b border-border bg-muted/30 pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <Layout className="h-5 w-5 text-primary" />
              Builder Tools
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 overflow-y-auto flex-1">
            <div className="space-y-6">
              <div>
                <label className="text-sm font-semibold text-foreground mb-2 block">Form Settings</label>
                <Input 
                  value={formName} 
                  onChange={(e) => setFormName(e.target.value)} 
                  className="font-medium"
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-foreground mb-3 block">Add Fields (Click to add)</label>
                <div className="grid grid-cols-2 gap-2">
                  {FIELD_TYPES.map((ft) => {
                    const Icon = ft.icon;
                    return (
                      <Button 
                        key={ft.type} 
                        variant="outline" 
                        className="justify-start gap-2 h-10 px-3 bg-card hover:bg-primary/5 hover:text-primary hover:border-primary/30 transition-all"
                        onClick={() => addField(ft)}
                      >
                        <Icon className="h-4 w-4 shrink-0 text-muted-foreground" />
                        <span className="text-xs truncate">{ft.label}</span>
                        <Plus className="h-3 w-3 ml-auto opacity-50 shrink-0" />
                      </Button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="text-sm font-semibold text-foreground mb-3 block">Field Configuration</label>
                {fields.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic bg-muted/30 p-3 rounded-md">Select a field above to configure it.</p>
                ) : (
                  <div className="space-y-3">
                    {fields.map((f, i) => (
                      <div key={f.id} className="p-3 border border-border rounded-md bg-card group relative">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-semibold text-muted-foreground uppercase">Field {i+1}</span>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-5 w-5 text-destructive/70 hover:text-destructive hover:bg-destructive/10"
                            onClick={() => removeField(f.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                        <div className="space-y-2">
                          <Input 
                            value={f.label} 
                            onChange={(e) => {
                              const newFields = [...fields];
                              newFields[i].label = e.target.value;
                              setFields(newFields);
                            }}
                            className="h-8 text-sm"
                            placeholder="Field Label"
                          />
                          {(f.type === 'text' || f.type === 'email' || f.type === 'tel' || f.type === 'textarea') && (
                            <Input 
                              value={f.placeholder || ""} 
                              onChange={(e) => {
                                const newFields = [...fields];
                                newFields[i].placeholder = e.target.value;
                                setFields(newFields);
                              }}
                              className="h-8 text-sm bg-muted/30"
                              placeholder="Placeholder"
                            />
                          )}
                          <div className="flex items-center gap-2 mt-2">
                            <input 
                              type="checkbox" 
                              id={`req-${f.id}`}
                              checked={f.required}
                              onChange={(e) => {
                                const newFields = [...fields];
                                newFields[i].required = e.target.checked;
                                setFields(newFields);
                              }}
                              className="rounded border-muted-foreground text-primary focus:ring-primary h-3 w-3"
                            />
                            <label htmlFor={`req-${f.id}`} className="text-xs text-muted-foreground">Required Field</label>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Right Column: Live Preview */}
        <Card className="lg:col-span-8 flex flex-col bg-muted/10 border-dashed border-2 h-[600px] lg:h-auto overflow-hidden">
          <CardHeader className="border-b border-border/50 bg-card/50 pb-3 shrink-0 flex flex-row items-center justify-between">
            <CardTitle className="text-sm text-muted-foreground font-medium flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Live Preview
            </CardTitle>
            <Badge variant="outline" className="bg-background">Desktop View</Badge>
          </CardHeader>
          <CardContent className="flex-1 flex items-center justify-center p-6 sm:p-12 overflow-y-auto">
            
            {/* The Actual Form Preview rendered as it would appear embedded */}
            <div className="w-full max-w-md bg-card shadow-xl rounded-xl border border-border p-6 sm:p-8 animate-in fade-in zoom-in-95 duration-300">
              <div className="mb-6">
                <h3 className="text-2xl font-bold text-foreground mb-2">{formName}</h3>
                <p className="text-sm text-muted-foreground">Please fill out the form below and our team will get in touch.</p>
              </div>

              <div className="space-y-4">
                {fields.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground bg-muted/20 border border-dashed border-muted rounded-lg">
                    Add fields from the builder to see them here.
                  </div>
                ) : (
                  fields.map((f) => (
                    <div key={f.id} className="space-y-1.5 transition-all duration-300">
                      <label className="text-sm font-medium text-foreground">
                        {f.label} {f.required && <span className="text-destructive">*</span>}
                      </label>
                      
                      {f.type === "textarea" ? (
                        <textarea 
                          placeholder={f.placeholder} 
                          className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50" 
                        />
                      ) : f.type === "select" ? (
                        <select className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50">
                          <option>Option 1</option>
                          <option>Option 2</option>
                        </select>
                      ) : f.type === "checkbox" ? (
                        <div className="flex items-center gap-2 h-9">
                          <input type="checkbox" className="rounded border-muted-foreground text-primary focus:ring-primary h-4 w-4" />
                          <span className="text-sm text-muted-foreground">I agree to the terms</span>
                        </div>
                      ) : (
                        <Input type={f.type} placeholder={f.placeholder} />
                      )}
                    </div>
                  ))
                )}
              </div>

              <Button className="w-full mt-6 h-11 shadow-md bg-gradient-to-r from-primary to-indigo-600 hover:from-primary/90 hover:to-indigo-600/90 text-white font-semibold">
                Submit
              </Button>
            </div>
            
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
