import customtkinter as ctk
import json
import os

C_BG     = "#09090B"
C_CARD   = "#18181B"
C_BORDER = "#27272A"
C_ACCENT = "#00E5FF"
C_TEXT   = "#FAFAFA"
C_MUTED  = "#A1A1AA"

class SettingsPanel(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=C_BG, **kwargs)

        self.settings_file = "data/settings.json"
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

        # Title
        ctk.CTkLabel(self, text="Global Configuration",
                     font=("Segoe UI Variable Display", 22, "bold"), text_color=C_TEXT).pack(pady=(28, 4), padx=30, anchor="w")
        ctk.CTkLabel(self, text="Adjust anti-ban timing and automation behavior",
                     font=("Segoe UI Variable Display", 13), text_color=C_MUTED).pack(pady=(0, 20), padx=30, anchor="w")

        # Organization Settings Card
        org_card = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        org_card.pack(fill="x", padx=30, pady=(0, 20))
        org_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(org_card, text="Organization Details", font=("Segoe UI Variable Display", 15, "bold"), text_color=C_ACCENT).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 8), sticky="w")

        def row(parent, r, label, default, hint="", is_text_box=False):
            ctk.CTkLabel(parent, text=label, font=("Segoe UI Variable Display", 13, "bold"), text_color=C_TEXT
                         ).grid(row=r*2, column=0, columnspan=2, padx=20, pady=(12, 2), sticky="w")
            if hint:
                ctk.CTkLabel(parent, text=hint, font=("Segoe UI Variable Display", 11), text_color=C_MUTED
                             ).grid(row=r*2, column=0, columnspan=2, padx=20, pady=(0, 0), sticky="e")
            
            if is_text_box:
                entry = ctk.CTkTextbox(parent, height=80, fg_color="#09090B",
                                     border_color=C_BORDER, border_width=1,
                                     text_color=C_TEXT, font=("Segoe UI Variable Display", 13))
                entry.insert("0.0", str(default))
            else:
                entry = ctk.CTkEntry(parent, height=36, fg_color="#09090B",
                                     border_color=C_BORDER, border_width=1,
                                     text_color=C_TEXT, font=("Segoe UI Variable Display", 13))
                entry.insert(0, str(default))
                
            entry.grid(row=r*2+1, column=0, columnspan=2, padx=20, pady=(4, 0), sticky="ew")
            return entry

        self.entry_company_name = row(org_card, 1, "Company Name", "সোনালী সৌরভ মাইগ্রেশন এ্যান্ড ভিসা", "Used in message templates")
        self.entry_contact_info = row(org_card, 2, "Contact Information", "01624-283260, 01619-949990", "Phone numbers for prospects to call")
        self.entry_address = row(org_card, 3, "Physical Address", "গ-১৩১/১, যুবরাজ ভিলা (২য় তলা), বাড্ডা লিঙ্ক রোড (প্রাণ সেন্টারের বিপরীতে), ঢাকা-১২১২", "Office address", is_text_box=True)

        ctk.CTkLabel(org_card, text="Campaign Theme", font=("Segoe UI Variable Display", 13, "bold"), text_color=C_TEXT).grid(row=8, column=0, columnspan=2, padx=20, pady=(12, 2), sticky="w")
        ctk.CTkLabel(org_card, text="Message tone & style", font=("Segoe UI Variable Display", 11), text_color=C_MUTED).grid(row=8, column=0, columnspan=2, padx=20, pady=(0, 0), sticky="e")
        self.entry_theme = ctk.CTkOptionMenu(org_card, values=["Default", "Friendly", "Urgent"], fg_color="#09090B", button_color=C_BORDER, text_color=C_TEXT, font=("Segoe UI Variable Display", 13))
        self.entry_theme.grid(row=9, column=0, columnspan=2, padx=20, pady=(4, 20), sticky="ew")

        # Automation Settings Card
        auto_card = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        auto_card.pack(fill="x", padx=30, pady=0)
        auto_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(auto_card, text="Automation Limits & Delays", font=("Segoe UI Variable Display", 15, "bold"), text_color=C_ACCENT).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 8), sticky="w")

        self.entry_daily_limit = row(auto_card, 1, "Daily Message Limit", 150, "Max messages before pausing (Safety feature)")
        self.entry_min_delay   = row(auto_card, 2, "Minimum Delay (seconds)", 25, "Between each message")
        self.entry_max_delay   = row(auto_card, 3, "Maximum Delay (seconds)", 55, "Random upper bound")
        self.entry_break_after = row(auto_card, 4, "Batch Size (messages)", 15, "Messages before break")

        # Break duration — two fields side by side
        ctk.CTkLabel(auto_card, text="Break Duration (seconds)", font=("Arial", 13, "bold"), text_color=C_TEXT
                     ).grid(row=10, column=0, columnspan=2, padx=20, pady=(16, 2), sticky="w")
        ctk.CTkLabel(auto_card, text="Min → Max", font=("Arial", 10), text_color=C_MUTED
                     ).grid(row=10, column=1, padx=20, pady=(16, 2), sticky="e")

        dur_frame = ctk.CTkFrame(auto_card, fg_color="transparent")
        dur_frame.grid(row=11, column=0, columnspan=2, padx=20, pady=(4, 20), sticky="ew")
        dur_frame.grid_columnconfigure((0,1), weight=1)

        self.entry_break_min = ctk.CTkEntry(dur_frame, height=36, fg_color="#0D1117",
                                            border_color=C_BORDER, border_width=1,
                                            text_color=C_TEXT, font=("Arial", 13),
                                            placeholder_text="Min (300)")
        self.entry_break_min.insert(0, "300")
        self.entry_break_min.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.entry_break_max = ctk.CTkEntry(dur_frame, height=36, fg_color="#0D1117",
                                            border_color=C_BORDER, border_width=1,
                                            text_color=C_TEXT, font=("Arial", 13),
                                            placeholder_text="Max (600)")
        self.entry_break_max.insert(0, "600")
        self.entry_break_max.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # AI Configuration Card
        ai_card = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=12, border_width=1, border_color=C_BORDER)
        ai_card.pack(fill="x", padx=30, pady=(20, 0))
        ai_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(ai_card, text="AI Smart Reply (Gemini)", font=("Segoe UI Variable Display", 15, "bold"), text_color="#8B5CF6").grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 8), sticky="w")
        
        self.entry_gemini_api_key = row(ai_card, 1, "Gemini API Key", "", "Leave empty to disable Smart Reply")
        self.entry_bot_context = row(ai_card, 2, "Bot Context / Behavior", "You are a helpful assistant for a migration agency. Be polite, brief, and try to answer basic questions about visa processing.", "Instructions for how the AI should respond", is_text_box=True)

        # Apply Button
        self.btn_save = ctk.CTkButton(self, text="✔  APPLY CHANGES",
                                      font=("Segoe UI Variable Display", 14, "bold"),
                                      command=self._save_settings,
                                      fg_color="#3B82F6", hover_color="#2563EB",
                                      text_color="#FAFAFA", height=46, corner_radius=10)
        self.btn_save.pack(pady=24, padx=30, fill="x")

        self.lbl_status = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color=C_ACCENT)
        self.lbl_status.pack()

        # Load existing settings
        self._load_settings()

    def _load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                def set_val(entry, key, is_text_box=False):
                    if key in data:
                        if is_text_box:
                            entry.delete("0.0", "end")
                            entry.insert("0.0", str(data[key]))
                        else:
                            entry.delete(0, "end")
                            entry.insert(0, str(data[key]))

                set_val(self.entry_company_name, "company_name")
                set_val(self.entry_contact_info, "contact_info")
                set_val(self.entry_address, "address", is_text_box=True)
                
                if "theme" in data:
                    self.entry_theme.set(str(data["theme"]))
                    
                set_val(self.entry_daily_limit, "daily_limit")
                set_val(self.entry_min_delay, "min_delay")
                set_val(self.entry_max_delay, "max_delay")
                set_val(self.entry_break_after, "break_after")
                set_val(self.entry_break_min, "break_min")
                set_val(self.entry_break_max, "break_max")
                set_val(self.entry_gemini_api_key, "gemini_api_key")
                set_val(self.entry_bot_context, "bot_context", is_text_box=True)
            except Exception as e:
                print(f"Failed to load settings: {e}")

    def _save_settings(self):
        data = self.get_settings()
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.lbl_status.configure(text="✔  Settings saved successfully!")
            self.after(3000, lambda: self.lbl_status.configure(text=""))
        except Exception as e:
            self.lbl_status.configure(text=f"✖  Failed to save: {str(e)}", text_color="#F85149")
            self.after(3000, lambda: self.lbl_status.configure(text="", text_color=C_ACCENT))

    def get_settings(self):
        try:
            return {
                'company_name': self.entry_company_name.get().strip(),
                'contact_info': self.entry_contact_info.get().strip(),
                'address': self.entry_address.get("0.0", "end").strip(),
                'theme': self.entry_theme.get(),
                'daily_limit': int(self.entry_daily_limit.get() or 150),
                'min_delay':   int(self.entry_min_delay.get() or 25),
                'max_delay':   int(self.entry_max_delay.get() or 55),
                'break_after': int(self.entry_break_after.get() or 15),
                'break_min':   int(self.entry_break_min.get() or 300),
                'break_max':   int(self.entry_break_max.get() or 600),
                'gemini_api_key': self.entry_gemini_api_key.get().strip(),
                'bot_context': self.entry_bot_context.get("0.0", "end").strip(),
            }
        except ValueError:
            return {
                'company_name': "সোনালী সৌরভ মাইগ্রেশন এ্যান্ড ভিসা",
                'contact_info': "01624-283260, 01619-949990",
                'address': "গ-১৩১/১, যুবরাজ ভিলা (২য় তলা), বাড্ডা লিঙ্ক রোড (প্রাণ সেন্টারের বিপরীতে), ঢাকা-১২১২",
                'theme': "Default",
                'daily_limit': 150, 
                'min_delay': 25, 
                'max_delay': 55, 
                'break_after': 15, 
                'break_min': 300, 
                'break_max': 600,
                'gemini_api_key': "",
                'bot_context': "You are a helpful assistant for a migration agency. Be polite, brief, and try to answer basic questions about visa processing."
            }
