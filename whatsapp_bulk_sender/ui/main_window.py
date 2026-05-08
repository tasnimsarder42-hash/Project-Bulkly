# pyrefly: ignore [missing-import]
import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
import threading
import os
from PIL import Image

from core.excel_reader import ExcelReader
from core.message_generator import MessageGenerator
from core.whatsapp_sender import WhatsAppSender
from core.session_manager import SessionManager
from ui.lead_table import LeadTable
from ui.dashboard import Dashboard
from ui.settings_panel import SettingsPanel

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setup Window
        self.title("Bulkly - Smart Bulk WhatsApp")
        self.geometry("1100x750")
        self.minsize(900, 650)
        
        # Set Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")
        
        # Premium Dynamic Color Palette
        self.C_BG       = "#09090B"   # Deep Space Background
        self.C_SIDEBAR  = "#121214"   # Sleek Sidebar
        self.C_CARD     = "#18181B"   # Elevated Cards
        self.C_BORDER   = "#27272A"   # Subtle Borders
        self.C_ACCENT   = "#00E5FF"   # Neon Teal Accent
        self.C_TEXT     = "#FAFAFA"   # Pure White Text
        self.C_MUTED    = "#A1A1AA"   # Muted Gray
        self.C_HOVER    = "#27272A"   # Interactive Hover
        self.C_SUCCESS  = "#10B981"   # Emerald Green
        self.C_DANGER   = "#EF4444"   # Vibrant Red
        self.C_WARNING  = "#F59E0B"   # Amber
        self.C_BLUE     = "#3B82F6"   # Electric Blue
        self.C_PURPLE   = "#8B5CF6"   # Deep Purple
        self.configure(fg_color=self.C_BG)
        
        # Core modules
        self.excel_reader = ExcelReader()
        self.message_generator = MessageGenerator()
        self.session_manager = SessionManager()
        self.whatsapp_sender = WhatsAppSender(ui_callback=self._on_whatsapp_status_update, log_callback=self._log_terminal)
        
        # State
        self.current_excel_path = None
        self.leads = []
        
        # Configure Grid Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.C_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        # row 0: Logo icon image
        try:
            logo_path = self.message_generator._resource_path("assets/logo.png")
            raw = Image.open(logo_path).convert("RGBA")
            # Replace near-white pixels with transparent
            data = raw.getdata()
            new_data = []
            for r, g, b, a in data:
                if r > 200 and g > 200 and b > 200:
                    new_data.append((r, g, b, 0))
                else:
                    new_data.append((r, g, b, a))
            raw.putdata(new_data)
            logo_img = ctk.CTkImage(light_image=raw, dark_image=raw, size=(72, 72))
            self.logo_icon = ctk.CTkLabel(self.sidebar_frame, image=logo_img, text="", fg_color="transparent")
            self.logo_icon.grid(row=0, column=0, padx=20, pady=(28, 0))
        except:
            pass

        # row 1: App name
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Bulkly", font=("Segoe UI Variable Display", 28, "bold"), text_color=self.C_ACCENT)
        self.logo_label.grid(row=1, column=0, padx=20, pady=(6, 0))

        # row 2: Tagline
        self.tagline_label = ctk.CTkLabel(self.sidebar_frame, text="Omnichannel Hub", font=("Segoe UI Variable Display", 11), text_color=self.C_MUTED)
        self.tagline_label.grid(row=2, column=0, padx=20, pady=(0, 24))

        # Separator
        sep = ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=self.C_BORDER)
        sep.grid(row=2, column=0, sticky="ew", padx=16, pady=(30, 8))

        # row 3-5: Nav buttons
        nav_font = ("Segoe UI Variable Display", 13, "bold")
        self.btn_nav_leads = ctk.CTkButton(self.sidebar_frame, text="  ⬡  Leads", command=lambda: self.select_frame("leads"),
                                           fg_color="transparent", text_color=self.C_TEXT, hover_color=self.C_HOVER,
                                           anchor="w", height=42, font=nav_font, corner_radius=8)
        self.btn_nav_leads.grid(row=3, column=0, padx=10, pady=2, sticky="ew")

        self.btn_nav_send = ctk.CTkButton(self.sidebar_frame, text="  ⬡  Automation", command=lambda: self.select_frame("send"),
                                          fg_color="transparent", text_color=self.C_TEXT, hover_color=self.C_HOVER,
                                          anchor="w", height=42, font=nav_font, corner_radius=8)
        self.btn_nav_send.grid(row=4, column=0, padx=10, pady=2, sticky="ew")

        self.btn_nav_settings = ctk.CTkButton(self.sidebar_frame, text="  ⬡  Settings", command=lambda: self.select_frame("settings"),
                                              fg_color="transparent", text_color=self.C_TEXT, hover_color=self.C_HOVER,
                                              anchor="w", height=42, font=nav_font, corner_radius=8)
        self.btn_nav_settings.grid(row=5, column=0, padx=10, pady=2, sticky="ew")

        # row 6: Divider label
        sep2 = ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=self.C_BORDER)
        sep2.grid(row=6, column=0, sticky="ew", padx=16, pady=12)

        # row 7 & 8: Spacer
        self.spacer = ctk.CTkFrame(self.sidebar_frame, height=40, fg_color="transparent")
        self.spacer.grid(row=7, column=0, sticky="ew", pady=10)

        # row 9: Theme switcher at bottom
        self.btn_theme = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"],
                                           command=self.change_appearance_mode_event,
                                           fg_color=self.C_CARD, button_color=self.C_HOVER,
                                           text_color=self.C_MUTED, font=("Arial", 11))
        self.btn_theme.grid(row=9, column=0, padx=12, pady=16, sticky="ew")

        # --- Main Content Frames ---
        self.frames = {}
        
        # 1. Leads Frame
        self.frames["leads"] = ctk.CTkFrame(self, corner_radius=0, fg_color=self.C_BG)
        self.frames["leads"].grid_rowconfigure(2, weight=1)
        self.frames["leads"].grid_columnconfigure(0, weight=1)

        # Page header
        leads_header = ctk.CTkLabel(self.frames["leads"], text="Lead Management",
                                    font=("Segoe UI Variable Display", 22, "bold"), text_color=self.C_TEXT)
        leads_header.grid(row=0, column=0, padx=24, pady=(20, 0), sticky="w")

        btn_bar = ctk.CTkFrame(self.frames["leads"], fg_color="transparent")
        btn_bar.grid(row=1, column=0, padx=20, pady=12, sticky="ew")

        self.btn_import = ctk.CTkButton(btn_bar, text="⬆  Import Excel", command=self.import_excel,
                                        fg_color=self.C_ACCENT, hover_color="#00B8D4", text_color="#09090B",
                                        font=("Segoe UI Variable Display", 13, "bold"), height=40, corner_radius=10)
        self.btn_import.pack(side="left", padx=(0, 10))

        self.btn_export = ctk.CTkButton(btn_bar, text="⬇  Export Results", command=self.export_results,
                                        fg_color=self.C_CARD, hover_color=self.C_HOVER, text_color=self.C_TEXT,
                                        border_color=self.C_BORDER, border_width=1,
                                        font=("Segoe UI Variable Display", 13), height=40, corner_radius=10)
        self.btn_export.pack(side="left")
        
        self.lead_table = LeadTable(self.frames["leads"])
        self.lead_table.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # 2. Send Dashboard Frame
        self.frames["send"] = ctk.CTkFrame(self, corner_radius=0, fg_color=self.C_BG)
        self.frames["send"].grid_rowconfigure(1, weight=1)
        self.frames["send"].grid_columnconfigure(0, weight=1)

        # Page header
        send_header = ctk.CTkLabel(self.frames["send"], text="Automation Center",
                                   font=("Segoe UI Variable Display", 22, "bold"), text_color=self.C_TEXT)
        send_header.grid(row=0, column=0, padx=24, pady=(20, 0), sticky="w")
        
        self.dashboard = Dashboard(self.frames["send"], control_callbacks={
            'start': self.start_sending,
            'pause': self.pause_sending,
            'resume': self.resume_sending,
            'stop': self.stop_sending,
            'add_to_group': self.start_group_add
        })
        self.dashboard.grid(row=0, column=0, sticky="ew", padx=20, pady=(55, 0))
        
        # Log terminal
        self.log_textbox = ctk.CTkTextbox(self.frames["send"], fg_color=self.C_CARD, text_color=self.C_TEXT,
                                          font=("Courier New", 11), corner_radius=8,
                                          border_color=self.C_BORDER, border_width=1)
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(8, 20))
        self.log_textbox.insert("0.0", "─── Activity Log ───\n")
        self.log_textbox.configure(state="disabled")

        # 3. Settings Frame
        self.frames["settings"] = ctk.CTkFrame(self, corner_radius=0, fg_color=self.C_BG)
        self.settings_panel = SettingsPanel(self.frames["settings"])
        self.settings_panel.pack(fill="both", expand=True)

        # Initialize default view
        self.select_frame("leads")
        
        # Check for previous session
        self.check_previous_session()

    def select_frame(self, name):
        # Hide all frames
        for frame in self.frames.values():
            frame.grid_forget()
        # Show selected frame
        self.frames[name].grid(row=0, column=1, sticky="nsew")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def import_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            self.load_excel(file_path)

    def load_excel(self, file_path):
        leads, err = self.excel_reader.read_leads(file_path)
        if err:
            messagebox.showerror("Error", f"Failed to read Excel: {err}")
            return
            
        self.leads = leads
        self.current_excel_path = file_path
        self.lead_table.load_data(self.leads)
        self.update_dashboard_stats()
        self.session_manager.save_session(self.leads, self.current_excel_path)
        messagebox.showinfo("Success", f"Loaded {len(self.leads)} valid leads.")

    def update_dashboard_stats(self):
        total = len(self.leads)
        sent = sum(1 for l in self.leads if l.get('status') == 'Sent')
        failed = sum(1 for l in self.leads if l.get('status') == 'Failed')
        pending = total - sent - failed
        self.dashboard.update_stats(total, sent, failed, pending)

    def export_results(self):
        if not self.current_excel_path or not self.leads:
            messagebox.showwarning("Warning", "No data to export.")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if save_path:
            success, err = self.excel_reader.export_results(self.current_excel_path, self.leads, save_path)
            if success:
                messagebox.showinfo("Success", "Results exported successfully.")
            else:
                messagebox.showerror("Error", f"Failed to export: {err}")

    # --- WhatsApp Sender Controls ---
    def start_sending(self, platform="WhatsApp"):
        if not self.leads:
            messagebox.showwarning("Warning", "No leads imported.")
            self.dashboard.reset_ui()
            return
            
        settings = self.settings_panel.get_settings()
        
        # Run in thread
        self.send_thread = threading.Thread(target=self._run_sending_process, args=(settings, platform))
        self.send_thread.daemon = True
        self.send_thread.start()

    def _run_sending_process(self, settings, platform="WhatsApp"):
        # Extract custom properties from settings
        company_name = settings.get('company_name', '')
        contact_info = settings.get('contact_info', '')
        address = settings.get('address', '')

        # We wrap the call to inject the dynamic details
        original_gen = self.message_generator.generate_message
        self.message_generator.generate_message = lambda lead: original_gen(
            lead, 
            company_name=company_name, 
            contact_info=contact_info, 
            address=address
        )
        
        try:
            if platform == "Telegram":
                from core.platform_connectors import TelegramConnector
                connector = TelegramConnector(credentials=settings)
                connector.connect()
                self._log_terminal("Telegram Connector initialized. Running stub...")
                time.sleep(2)
                for lead in self.leads:
                    if lead.get('status') not in ['Sent', 'Failed']:
                        msg = self.message_generator.generate_message(lead)
                        connector.send_message(lead.get('phone', 'Unknown'), msg)
                        self._on_whatsapp_status_update(lead.get('id'), "Sent")
                        time.sleep(1)
                connector.disconnect()
                self._on_whatsapp_status_update("SYSTEM", "COMPLETED")
                
            elif platform == "Instagram":
                from core.platform_connectors import InstagramConnector
                connector = InstagramConnector(credentials=settings)
                connector.connect()
                self._log_terminal("Instagram Connector initialized. Running stub...")
                time.sleep(2)
                for lead in self.leads:
                    if lead.get('status') not in ['Sent', 'Failed']:
                        msg = self.message_generator.generate_message(lead)
                        connector.send_message(lead.get('phone', 'Unknown'), msg)
                        self._on_whatsapp_status_update(lead.get('id'), "Sent")
                        time.sleep(1)
                connector.disconnect()
                self._on_whatsapp_status_update("SYSTEM", "COMPLETED")
                
            elif platform == "Messenger":
                from core.platform_connectors import MessengerConnector
                connector = MessengerConnector(credentials=settings)
                connector.connect()
                self._log_terminal("Messenger Connector initialized. Running stub...")
                time.sleep(2)
                for lead in self.leads:
                    if lead.get('status') not in ['Sent', 'Failed']:
                        msg = self.message_generator.generate_message(lead)
                        connector.send_message(lead.get('phone', 'Unknown'), msg)
                        self._on_whatsapp_status_update(lead.get('id'), "Sent")
                        time.sleep(1)
                connector.disconnect()
                self._on_whatsapp_status_update("SYSTEM", "COMPLETED")
                
            elif platform == "Threads":
                from core.platform_connectors import ThreadsConnector
                connector = ThreadsConnector(credentials=settings)
                connector.connect()
                self._log_terminal("Threads Connector initialized. Running stub...")
                time.sleep(2)
                for lead in self.leads:
                    if lead.get('status') not in ['Sent', 'Failed']:
                        msg = self.message_generator.generate_message(lead)
                        connector.send_message(lead.get('phone', 'Unknown'), msg)
                        self._on_whatsapp_status_update(lead.get('id'), "Sent")
                        time.sleep(1)
                connector.disconnect()
                self._on_whatsapp_status_update("SYSTEM", "COMPLETED")
                
            else:
                self.whatsapp_sender.send_messages(self.leads, self.message_generator, settings)
                
        finally:
            # Restore original generator after session
            self.message_generator.generate_message = original_gen

    def pause_sending(self):
        self.whatsapp_sender.pause()

    def resume_sending(self):
        self.whatsapp_sender.resume()

    def stop_sending(self):
        self.whatsapp_sender.stop()

    def start_group_add(self, group_name):
        if not self.leads:
            messagebox.showwarning("Warning", "No leads imported.")
            self.dashboard.reset_ui()
            return
            
        pending_leads = [lead['phone'] for lead in self.leads if lead.get('status') not in ['Sent', 'Failed']]
        if not pending_leads:
            messagebox.showwarning("Warning", "No pending leads to add to group.")
            self.dashboard.reset_ui()
            return
            
        # Run in thread
        self.send_thread = threading.Thread(target=self._run_group_add_process, args=(group_name, pending_leads))
        self.send_thread.daemon = True
        self.send_thread.start()
        
    def _run_group_add_process(self, group_name, pending_phones):
        try:
            self.whatsapp_sender.add_to_group(group_name, pending_phones)
        except Exception as e:
            self._log_terminal(f"Error adding to group: {e}")

    def _on_whatsapp_status_update(self, lead_id, status):
        # This is called from the sender thread, so we must schedule UI updates safely
        self.after(0, self._update_ui_state, lead_id, status)

    def _update_ui_state(self, lead_id, status):
        if str(lead_id).startswith("SYSTEM"):
            if status == "COMPLETED":
                messagebox.showinfo("Done", "All messages processed.")
                self.dashboard.reset_ui()
            return
            
        # Update table and stats
        self.lead_table.update_lead_status(lead_id, status)
        self.update_dashboard_stats()
        
        # Save session periodically (every 5 sends to avoid disk spam)
        sent_count = sum(1 for l in self.leads if l.get('status') == 'Sent')
        if sent_count % 5 == 0:
            self.session_manager.save_session(self.leads, self.current_excel_path)

    def _log_terminal(self, msg):
        self.after(0, self._insert_log, msg)

    def _insert_log(self, msg):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", msg + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def check_previous_session(self):
        excel_path, leads = self.session_manager.load_session()
        if excel_path and leads:
            answer = messagebox.askyesno("Resume Session", "A previous session was found. Do you want to resume it?")
            if answer:
                self.current_excel_path = excel_path
                self.leads = leads
                self.lead_table.load_data(self.leads)
                self.update_dashboard_stats()
            else:
                self.session_manager.clear_session()
                
    def on_closing(self):
        if self.whatsapp_sender.is_running:
            if messagebox.askokcancel("Quit", "Sending is in progress. Do you want to quit?"):
                self.whatsapp_sender.stop()
                self.whatsapp_sender.close()
                self.destroy()
        else:
            self.whatsapp_sender.close()
            self.destroy()
