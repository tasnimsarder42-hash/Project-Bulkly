import customtkinter as ctk

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, control_callbacks, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.control_callbacks = control_callbacks
        self.grid_columnconfigure(0, weight=1)

        # --- Omnichannel Platform Selector ---
        platform_frame = ctk.CTkFrame(self, fg_color="transparent")
        platform_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        
        ctk.CTkLabel(platform_frame, text="Active Platform", font=("Segoe UI Variable Display", 14, "bold"), text_color="#00E5FF").pack(side="left", padx=(6, 20))
        
        self.selected_platform = ctk.StringVar(value="WhatsApp")
        
        self.seg_platform = ctk.CTkSegmentedButton(platform_frame, values=["WhatsApp", "Telegram", "Instagram", "Messenger", "Threads"],
                                                   variable=self.selected_platform,
                                                   font=("Segoe UI Variable Display", 13, "bold"),
                                                   fg_color="#18181B",
                                                   selected_color="#00E5FF",
                                                   selected_hover_color="#00B8D4",
                                                   unselected_color="#18181B",
                                                   unselected_hover_color="#27272A",
                                                   text_color="#FAFAFA")
        self.seg_platform.pack(side="left")

        # --- Stat Cards ---
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(8, 0))
        cards_frame.grid_columnconfigure((0,1,2,3), weight=1)

        def make_stat_card(parent, col, title, color):
            card = ctk.CTkFrame(parent, fg_color="#18181B", corner_radius=12, border_width=1, border_color="#27272A")
            card.grid(row=0, column=col, padx=6, pady=0, sticky="ew")
            # Colored accent top bar
            accent = ctk.CTkFrame(card, fg_color=color, height=3, corner_radius=3)
            accent.pack(fill="x", padx=12, pady=(10, 6))
            val_lbl = ctk.CTkLabel(card, text="0", font=("Segoe UI Variable Display", 32, "bold"), text_color="#FAFAFA")
            val_lbl.pack(pady=(4, 0))
            ttl_lbl = ctk.CTkLabel(card, text=title, font=("Segoe UI Variable Display", 11, "bold"), text_color=color)
            ttl_lbl.pack(pady=(0, 14))
            return val_lbl

        self.lbl_total   = make_stat_card(cards_frame, 0, "TOTAL",   "#3B82F6")
        self.lbl_sent    = make_stat_card(cards_frame, 1, "SENT",    "#10B981")
        self.lbl_failed  = make_stat_card(cards_frame, 2, "FAILED",  "#EF4444")
        self.lbl_pending = make_stat_card(cards_frame, 3, "PENDING", "#F59E0B")

        # --- Progress Bar ---
        prog_frame = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=12, border_width=1, border_color="#27272A")
        prog_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(16, 0))

        self.progress_label = ctk.CTkLabel(prog_frame, text="Status: Idle",
                                           font=("Segoe UI Variable Display", 13, "bold"), text_color="#A1A1AA")
        self.progress_label.pack(pady=(12, 4), padx=16, anchor="w")

        self.progress_bar = ctk.CTkProgressBar(prog_frame, height=8, corner_radius=4,
                                               progress_color="#00E5FF", fg_color="#27272A")
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 12))
        self.progress_bar.set(0)

        # --- Control Buttons ---
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=3, column=0, pady=(16, 0))

        btn_style = {"height": 44, "corner_radius": 10, "font": ("Segoe UI Variable Display", 13, "bold")}

        self.btn_start = ctk.CTkButton(controls_frame, text="▶  START AUTOMATION",
                                       command=self._on_start,
                                       fg_color="#00E5FF", hover_color="#00B8D4", text_color="#09090B",
                                       **btn_style)
        self.btn_start.pack(side="left", padx=8)

        self.btn_pause = ctk.CTkButton(controls_frame, text="⏸  PAUSE",
                                       command=self._on_pause,
                                       fg_color="#F59E0B", hover_color="#D97706", text_color="#09090B",
                                       state="disabled", **btn_style)
        self.btn_pause.pack(side="left", padx=8)

        self.btn_resume = ctk.CTkButton(controls_frame, text="▶▶  RESUME",
                                        command=self._on_resume,
                                        fg_color="#3B82F6", hover_color="#2563EB", text_color="#FAFAFA",
                                        state="disabled", **btn_style)
        self.btn_resume.pack(side="left", padx=8)

        self.btn_stop = ctk.CTkButton(controls_frame, text="■  STOP",
                                      command=self._on_stop,
                                      fg_color="#EF4444", hover_color="#DC2626", text_color="#FAFAFA",
                                      state="disabled", **btn_style)
        self.btn_stop.pack(side="left", padx=8)

        # --- Community Builder ---
        community_frame = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=12, border_width=1, border_color="#27272A")
        community_frame.grid(row=4, column=0, sticky="ew", padx=0, pady=(24, 0))
        
        ctk.CTkLabel(community_frame, text="Community Builder", font=("Segoe UI Variable Display", 15, "bold"), text_color="#8B5CF6").pack(pady=(16, 4), padx=20, anchor="w")
        ctk.CTkLabel(community_frame, text="Batch add pending leads to a WhatsApp group", font=("Segoe UI Variable Display", 12), text_color="#A1A1AA").pack(pady=(0, 16), padx=20, anchor="w")
        
        inner_comm_frame = ctk.CTkFrame(community_frame, fg_color="transparent")
        inner_comm_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.entry_group_name = ctk.CTkEntry(inner_comm_frame, placeholder_text="Exact WhatsApp Group Name", height=42, fg_color="#09090B", border_color="#27272A", font=("Segoe UI Variable Display", 13))
        self.entry_group_name.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        self.btn_add_group = ctk.CTkButton(inner_comm_frame, text="✚  ADD PENDING LEADS", height=42, font=("Segoe UI Variable Display", 12, "bold"), fg_color="#8B5CF6", hover_color="#7C3AED", text_color="#FAFAFA", command=self._on_add_to_group)
        self.btn_add_group.pack(side="right")

    def update_stats(self, total, sent, failed, pending):
        self.lbl_total.configure(text=str(total))
        self.lbl_sent.configure(text=str(sent))
        self.lbl_failed.configure(text=str(failed))
        self.lbl_pending.configure(text=str(pending))
        if total > 0:
            progress = (sent + failed) / total
            self.progress_bar.set(progress)
            self.progress_label.configure(text=f"Progress: {int(progress * 100)}%  ({sent} sent / {total} total)",
                                          text_color="#E6EDF3")

    def _on_start(self):
        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        self.btn_stop.configure(state="normal")
        if self.control_callbacks.get('start'):
            # Pass the selected platform to the start callback
            self.control_callbacks['start'](platform=self.selected_platform.get())

    def _on_pause(self):
        self.btn_pause.configure(state="disabled")
        self.btn_resume.configure(state="normal")
        if self.control_callbacks.get('pause'):
            self.control_callbacks['pause']()

    def _on_resume(self):
        self.btn_resume.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        if self.control_callbacks.get('resume'):
            self.control_callbacks['resume']()

    def _on_stop(self):
        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled")
        self.btn_resume.configure(state="disabled")
        self.btn_stop.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Status: Idle", text_color="#7D8590")
        if self.control_callbacks.get('stop'):
            self.control_callbacks['stop']()

    def _on_add_to_group(self):
        group_name = self.entry_group_name.get().strip()
        if group_name and self.control_callbacks.get('add_to_group'):
            self.control_callbacks['add_to_group'](group_name)

    def reset_ui(self):
        self._on_stop()
