import sys
import os
import multiprocessing

# Force project root into path for bundled executable reliability
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import customtkinter as ctk
from ui.main_window import MainWindow

def main():
    multiprocessing.freeze_support()
    # Set default appearance
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
