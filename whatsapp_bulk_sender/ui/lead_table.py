import customtkinter as ctk
from tkinter import ttk
import tkinter as tk

class LeadTable(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Search/Filter Frame
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Filter leads...", width=250, border_width=1, fg_color="#18181B", font=("Segoe UI Variable Display", 13))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self._filter_data)
        
        self.status_filter = ctk.CTkOptionMenu(self.filter_frame, values=["All", "Pending", "Sent", "Failed"], command=self._filter_data, fg_color="#18181B", button_color="#27272A", font=("Segoe UI Variable Display", 13))
        self.status_filter.pack(side="left", padx=5)
        
        # Style Treeview
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", 
                             background="#09090B",
                             foreground="#FAFAFA",
                             rowheight=35,
                             fieldbackground="#09090B",
                             borderwidth=0,
                             font=('Segoe UI Variable Display', 11))
        self.style.map('Treeview', background=[('selected', '#10B981')])
        self.style.configure("Treeview.Heading", 
                             background="#18181B", 
                             foreground="#A1A1AA", 
                             relief="flat",
                             font=('Segoe UI Variable Display', 11, 'bold'))

        # Treeview Scrollbar Frame
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview
        columns = ("ID", "Phone", "Experience", "Country", "Status")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        
        # Define headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Phone", text="PHONE")
        self.tree.heading("Experience", text="EXPERIENCE")
        self.tree.heading("Country", text="COUNTRY")
        self.tree.heading("Status", text="STATUS")
        
        # Define columns
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Phone", width=120, anchor="center")
        self.tree.column("Experience", width=150, anchor="w")
        self.tree.column("Country", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Data storage
        self.all_leads = []
        
        # Tag configurations for colors
        self.tree.tag_configure('Sent', foreground='#10B981')   
        self.tree.tag_configure('Failed', foreground='#EF4444') 
        self.tree.tag_configure('Pending', foreground='#F59E0B') 
        self.tree.tag_configure('In Progress', foreground='#3B82F6') 
        self.tree.tag_configure('oddrow', background='#18181B')
        self.tree.tag_configure('evenrow', background='#09090B')

    def load_data(self, leads):
        self.all_leads = leads
        self._populate_tree(self.all_leads)
        
    def _populate_tree(self, data):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for lead in data:
            status = lead.get('status', 'Pending')
            self.tree.insert("", "end", values=(
                lead.get('id', ''),
                lead.get('phone', ''),
                lead.get('experience', ''),
                lead.get('country', ''),
                status
            ), tags=(status,))
            
    def _filter_data(self, event=None):
        search_term = self.search_entry.get().lower()
        status_term = self.status_filter.get()
        
        filtered = []
        for lead in self.all_leads:
            match_search = (search_term in str(lead.get('phone', '')).lower() or 
                            search_term in str(lead.get('country', '')).lower() or
                            search_term in str(lead.get('experience', '')).lower())
            match_status = (status_term == "All" or lead.get('status', '') == status_term)
            
            if match_search and match_status:
                filtered.append(lead)
                
        self._populate_tree(filtered)

    def update_lead_status(self, lead_id, new_status):
        # Update internal data
        for lead in self.all_leads:
            if lead.get('id') == lead_id:
                lead['status'] = new_status
                break
                
        # Re-apply filter to update UI
        self._filter_data()
